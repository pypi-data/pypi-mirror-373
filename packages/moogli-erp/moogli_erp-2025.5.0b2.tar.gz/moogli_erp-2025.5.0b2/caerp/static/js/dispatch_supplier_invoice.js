/** Handles error state of inputs suposed to be linked through a sum compute
 *
 * One form field holds the total, and a collection of form fields holds the
 * lines to be summed up. This class checks in real time that the sum is right.
 *
 * This class checks the consistency on any of relevant fields edit and set
 * their validation state accordingly. This class only checks and does not
 * change fields value.
 */
class TotalMatchLinesValidation {
    /**
     * @param {string} lineFieldsSelector - the selector matching all sum members <input> elements
     * @param {jQuery} totalField - the ``<input>` containing the total
     * @param {jQuery} newLineButton - the DOM element that is already used to add a new form line to the invoice.
     */
    constructor(lineFieldsSelector, totalField, newLineButton) {
        this.lineFieldsSelector = lineFieldsSelector;
        this.totalField = totalField;
        this.newLineButton = newLineButton;

        this.install();
    }
    install() {
        this.watchFields();
        this.watchButton();
        this.update();
    }
    update() {
        let lines = $(this.lineFieldsSelector);
        let total = Number(this.totalField.val());
        let totalLines = 0;
        lines.each(i => totalLines += Number(lines[i].value));
        let errMsg = "Le total des lignes ne correspond pas à celui de la facture";

        if (total != totalLines.toFixed(5)) {
            lines.each(i => lines[i].setCustomValidity(errMsg));
            this.totalField.get(0).setCustomValidity(errMsg);
        } else {
            lines.each(i => lines[i].setCustomValidity(''));
            this.totalField.get(0).setCustomValidity('');
        }
    }

    getWatchedEls() {
        return this.totalField.add($(this.lineFieldsSelector));
    }
    unWatchFields() {
        this.getWatchedEls().off('change keyup');
    }
    watchFields() {
        let this_ = this;
        this.getWatchedEls().on('change keyup', function(event) {
            this_.update();
        });
    }
    watchButton() {
        let this_ = this;
        this.newLineButton.click(function(event) {
            // Include new line in watch scope
            this_.unWatchFields();
            this_.watchFields();
        });
    }

}
