let socket = new WebSocket("wss://" + window.location.host + "/ws");
let mySymbol = null;
let currentTurn = null;

/**
 * Mise à jour des informations sur le déroulement de la partie.
 *
 * @param {string} boardStr - Une chaîne de caractères représentant l'état du plateau de jeu.
 */
function updateStatus(boardStr) {
    if (!mySymbol) return;

    if (mySymbol === "S") {
      document.getElementById("turn").innerHTML = "C'est le tour du joueur (" + currentTurn + ")";
    }
    else {
      if (currentTurn === mySymbol) {
          document.getElementById("turn").innerHTML = "C'est votre tour";
      } else {
          if(boardStr === ",,,,,,,,") document.getElementById("turn").innerHTML = "En attente du joueur ( " + currentTurn + " )...";
          else document.getElementById("turn").innerHTML = "C'est le tour de votre adversaire";
      }
    }

    document.getElementById("user-msg").innerHTML = "Vous jouez: " + mySymbol;
}

/**
 * Mise à jour du tableau de jeu.
 *
 * @param {string} msg - Le message event.data recu par le websocket.
 */
function board_update(msg) {
  let [boardStr, current] = msg.split("|");
  currentTurn = current;
  updateStatus(boardStr);

  let cells = boardStr.split(",");
  let boxDivs = document.querySelectorAll(".cell");

  boxDivs.forEach((box, i) => {
      box.innerHTML = cells[i];
  });
}

/**
 * Gestion des messages reçus par le websocket et
 * soumission du formulaire pour accéder à la route /leaderboard.
 *
 * @param {MessageEvent} event - Le message recu par le websocket.
 */
socket.addEventListener("message", (event) => {
    let msg = event.data;

    // Assignation du symbole par le serveur.
    if (msg.startsWith("YOU|")) {
        mySymbol = msg.split("|")[1];
        document.getElementById("user-msg").innerHTML = "Vous êtes: " + mySymbol;
        return;
    }

    // Réception du message serveur en cas de déconnection.
    if (msg.startsWith("DISC|")) {
        disconnect = msg.split("|")[1];
        alert(disconnect);
        window.location.href = "https://" + window.location.host + "/";
        return;
    }

    // Réception du message serveur pour le gagnant.
    else if (msg.startsWith("WIN|")) {
        let winner = msg.split("|")[1];

        if(mySymbol === "X" || mySymbol === "O") {
          if (winner === mySymbol) {
              document.getElementById("result_value").value = "🎉 Victoire!";
          } else {
              document.getElementById("result_value").value = "You avez perdu… 💀";
          }
        }
        else {
          document.getElementById("result_value").value = "Le joueur " + winner + " remporte la partie! 🎉";
        }

        document.getElementById("result_form").submit();
        return;
    }

    else if (msg === "DRAW") {
        document.getElementById("result_value").value = "😐 Partie nulle!";
        document.getElementById("result_form").submit();
        return;
    }

    board_update(msg);
});

/**
 * Envoi du coup joué au serveur par le websocket.
 *
 * @param {PointerEvent} event - Événement représentant l'intercation de l'utilisateur.
 */
document.getElementById("board").addEventListener("click", function (event) {
    if (event.target.classList.contains("cell")) {
        const index = parseInt(event.target.dataset.index);
        if (!mySymbol) return;
        socket.send(index.toString());
    }
});
