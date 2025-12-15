// Selection de tous les champs dans les formulaires.
document.querySelectorAll("form input[type=text], form input[type=password]").forEach(function(input) {

     ["change", "invalid"].forEach(function(eventName) {
         input.addEventListener(eventName, function(event) {
             const field = event.target;

             // Effacer les messages précédents pour vérifier la validité.
             field.setCustomValidity("");

             // Si toujours invalide, on affiche le message.
             if (!field.validity.valid) {
                 field.setCustomValidity("Ce champ est requis et requiert 3 caractères au minimum.");
             }
         });
     });

});
