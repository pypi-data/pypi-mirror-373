/*

    Javascipt to handle utils interactions (menu, modals, ...)

*/


// UTILITY FUNCTIONS

function removeClass(el, cls) {
    var reg = new RegExp("(\\s|^)" + cls + "(\\s|$)");
    el.className = el.className.replace(reg, " ").replace(/(^\s*)|(\s*$)/g, "");
}

function addClass(el, cls) {
    el.className = el.className + " " + cls;
}

function hasClass(el, cls) {
    return el.className && new RegExp("(\\s|^)" + cls + "(\\s|$)").test(el.className);
}

function addEvent(obj, evType, fn) {
    // from http://onlinetools.org/articles/unobtrusivejavascript/chapter4.html
    if (obj.addEventListener) { obj.addEventListener(evType, fn, false); return true; }
    if (obj.attachEvent) { var r = obj.attachEvent("on" + evType, fn); return r; }
    return false;
}


// COOKIES FUNCTIONS

function setCookie(name, value, days) {
    var expires;
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    } else {
        expires = "";
    }
    document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + expires + "; path=/";
}

function getCookie(name) {
    var nameEQ = encodeURIComponent(name) + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) === ' ')
            c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0)
            return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
}

function unsetCookie(name) {
    setCookie(name, "", -1);
}


// SHOW / HIDE FUNCTIONS (MENUS, MODALS, DROPDOWNS...)

function toggleOpen(whichObject, callingObject) {
    var object = document.getElementById(whichObject);
    if (!object) object = whichObject;
    if (object.classList.contains('open')) {
        object.classList.remove('open');
        if (callingObject) {
            callingObject.title = callingObject.title.replace('Masquer', 'Afficher');
            callingObject.setAttribute("aria-label", callingObject.title);
            callingObject.setAttribute("aria-expanded", false);
        }
    } else {
        object.classList.add('open');
        if (callingObject) {
            callingObject.title = callingObject.title.replace('Afficher', 'Masquer');
            callingObject.setAttribute("aria-label", callingObject.title);
            callingObject.setAttribute("aria-expanded", true);
        }
        var formElements = object.elements;
        if (formElements) formElements[1].focus();
    }
    return false;
}

function toggleMenu(callingObject) {
    var callingButton = callingObject;
    var callingParent = callingButton.parentNode;
    var callingGrandParent = callingParent.parentNode;
    var callingGreatGrandParent = callingGrandParent.parentNode;
    var callingState = callingButton.getAttribute('aria-expanded').toString();
    var menuButtons = callingGrandParent.getElementsByTagName('BUTTON');
    var menuListItems = callingGrandParent.getElementsByTagName('LI');
    // 	close all siblings
    for (i = 0; i < menuButtons.length; i++) {
        menuButtons[i].setAttribute('aria-expanded', 'false');
        menuButtons[i].title = menuButtons[i].title.replace('Masquer', 'Afficher');
    }
    // expand clicked button submenu
    if (callingState == 'false') {
        callingButton.setAttribute('aria-expanded', 'true');
        callingButton.title = callingButton.title.replace('Afficher', 'Masquer');
    }
    var currentClass = 'current_menu';
    if (callingGreatGrandParent.tagName == "LI") {
        currentClass = 'current_submenu';
    }
    // remove current_submenu or current_menu class from all siblings
    for (i = 0; i < menuListItems.length; i++) {
        if (menuListItems[i].classList.contains(currentClass)) {
            menuListItems[i].classList.remove(currentClass);
        }
    }
    // add current_subemnu or current_menu class to parent
    if (callingState == 'false') {
        if (!callingParent.classList.contains(currentClass)) {
            callingParent.classList.add(currentClass);
        }
    }
}

function resize(object, callingObject) {
    var targetClass = object + "_mini";
    if (document.body.classList.contains(targetClass)) {
        document.body.classList.remove(targetClass);
        if (callingObject) {
            callingObject.title = callingObject.title.replace('Afficher', 'Réduire');
            callingObject.setAttribute("aria-label", callingObject.title);
        }
    }
    else {
        document.body.classList.add(targetClass);
        if (callingObject) {
            callingObject.title = callingObject.title.replace('Réduire', 'Afficher');
            callingObject.setAttribute("aria-label", callingObject.title);
        }
    }
    document.body.offsetHeight;
    setCookie('caerp__menu_mini', document.body.classList.contains(targetClass));
}

function toggleModal(whichModal) {
    var modalObject = document.getElementById(whichModal);
    var modalButtons = modalObject.getElementsByTagName('BUTTON');
    if (modalObject.style.display == 'none') {
        modalObject.setAttribute('style', 'display:flex;');
        modalObject.classList.remove('dismiss');
        document.body.classList.add('modal_open');
        modalObject.classList.add('appear');
        for (i = 0; i < modalButtons.length; i++) {
            if (modalButtons[i].classList.contains('main')) modalButtons[i].focus();
        }
        autofocusContent(modalObject);
    }
    else {
        modalObject.setAttribute('style', 'display:none;');
        document.body.classList.remove('modal_open');
        modalObject.classList.remove('appear');
        modalObject.classList.add('dismiss');
    }
}

function toggleCollapse(heading) {
    let btn;
    let target;
    let targetList;
    if (heading.classList.contains('collapse_button')) {
        btn = heading;
        let headingTarget = btn.dataset.collapseTarget;
        let selector = "[data-collapse-trigger*='" + headingTarget + "']";
        targetList = document.querySelectorAll(selector);
    }
    else if (heading.tagName == "A") {
        btn = heading;
        if (heading.classList.contains('dropdown-toggle')) {
            target = heading.nextElementSibling;
        }
        else {
            target = heading.parentNode.nextElementSibling;
        }
    }
    else {
        btn = heading.querySelector('a');
        target = heading.nextElementSibling;
    }
    let expanded = btn.getAttribute('aria-expanded') === 'true' || false;
    btn.setAttribute('aria-expanded', !expanded);
    let tooltip = btn.getAttribute('title');
    if (tooltip) {
        if (expanded) {
            btn.setAttribute('title', tooltip.replace('Masquer', 'Afficher'));
            btn.setAttribute('aria-label', tooltip.replace('Masquer', 'Afficher'));
        }
        else {
            btn.setAttribute('title', tooltip.replace('Afficher', 'Masquer'));
            btn.setAttribute('aria-label', tooltip.replace('Afficher', 'Masquer'));
        }
    }
    if (targetList) {
        for (let i = 0; i < targetList.length; i++) {
            let parentInfo = targetList[i].dataset.collapseParent;
            if (parentInfo && !expanded) {
                let parentSelector = "[data-collapse-target='" + parentInfo + "']";
                let parent = document.querySelector(parentSelector);
                let parentExpanded = parent.getAttribute('aria-expanded') === 'true' || false;
                if (parentExpanded) {
                    targetList[i].hidden = expanded;
                }
            }
            else {
                targetList[i].hidden = expanded;
            }
        }
    }
    else {
        target.hidden = expanded;
    }
}

function toggleTableFullscreen(button) {
    let tableContainer = button.parentNode;
    let buttonTextSpan = button.getElementsByTagName( 'SPAN' );

    if ( tableContainer.classList.contains( 'table_container' ) ) {
        if ( tableContainer.classList.contains( 'fullscreen' ) ) {
            tableContainer.classList.remove( 'fullscreen' );
            buttonTextSpan[0].innerHTML = "Plein écran";
            button.title = "Afficher le tableau en mode plein écran";
            button.ariaLabel = "Afficher le tableau en mode plein écran";
        }
        else {
            tableContainer.classList.add( 'fullscreen' );
            buttonTextSpan[0].innerHTML = "Normal";
            button.title = "Afficher le tableau en mode normal";
            button.ariaLabel = "Afficher le tableau en mode normal";
        }
    }
}