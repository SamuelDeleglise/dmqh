// Wait till the browser is ready to render the game (avoids glitches)
window.requestAnimationFrame(function () {
  var a = new GameManager(4, KeyboardInputManager, HTMLActuator, LocalStorageManager);

  var MAPPING = {
    i: 0,// top
    j: 3,// left
    k: 2,// down
    l: 1//right
  }

  a.inputManager.on("restart", guess);

  function guess() {
      $.post('/guess', {"game_state": localStorage.gameState}, function(result) {
            if (!a.won || !a.over) {
                a.move(MAPPING[result]);
                guess();
            }
      });
  }

  guess();

});
