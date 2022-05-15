var systemValves = ["valve1", "valve2", "valve3"];
var valveStates = {"valve1": false, "valve2": false, "valve3": false};

window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    initializationFunc: function initialize(_id) {
      var svg = document.getElementById("embedded-diagram").contentDocument;
      var pump = svg.getElementById("pumpImpellerAnimation");
      if (pump == null) {
        lazyTrigger(initPumpAnimation, 1000, 2);
      } else {
        initPumpAnimation();
      }

      var dirtWaterAnimation = document.getElementById("dirtWaterAnimation");
      console.log("State of dirtWaterAnimation: " + dirtWaterAnimation);
      if (dirtWaterAnimation == null) {
        lazyTrigger(initDirtWaterAnimation, 1000, 2);
      } else {
        initDirtWaterAnimation();
      }

      var waterMainValveExit = document.getElementById("mainValveExit");
      console.log("State of waterMainValveExit: " + waterMainValveExit);
      if (waterMainValveExit == null) {
        lazyTrigger(initWaterMainValveExitAnimation, 1000, 2);
      } else {
        initWaterMainValveExitAnimation();
      }

      var waterMainValveInlet = document.getElementById("mainValveInlet");
      console.log("State of waterMainValveInlet: " + waterMainValveInlet);
      if (waterMainValveInlet == null) {
        lazyTrigger(initWaterMainValveInlet, 1000, 2);
      } else {
        initWaterMainValveInlet();
      }

      var mainWaterTop = document.getElementById("mainWaterTop");
      console.log("State of mainWaterTop: " + mainWaterTop);
      if (mainWaterTop == null) {
        lazyTrigger(initMainWaterTop, 1000, 2);
      } else {
        initMainWaterTop();
      }

      var mainWaterDown = document.getElementById("mainWaterDown");
      console.log("State of mainWaterDown: " + mainWaterDown);
      if (mainWaterDown == null) {
        lazyTrigger(initMainWaterDown, 1000, 2);
      } else {
        initMainWaterDown();
      }

      var waterFeedMotion = document.getElementById("waterFeedMotion");
      console.log("State of waterFeedMotion: " + waterFeedMotion);
      if (waterFeedMotion == null) {
        lazyTrigger(initWaterFeedMotion, 1000, 2);
      } else {
        initWaterFeedMotion();
      }

      var secWaterMotion = document.getElementById("secWaterMotion");
      console.log("State of secWaterMotion: " + secWaterMotion);
      if (secWaterMotion == null) {
        lazyTrigger(initSecWaterMotion, 1000, 2);
      } else {
        initSecWaterMotion();
      }

      
      return _id;
    },
    toggleValve: toggleValve,
    switchPump: switchPump
  }
});

function switchPump(state) {
  var svg = document.getElementById("embedded-diagram").contentDocument;
  if (svg != null) {
    var pump = svg.getElementById("pumpImpeller");
    if (pump != null) {
      if (state) {
        pump.unpauseAnimations();
        checkWaterFlow(svg, state);
      } else {
        pump.pauseAnimations();
        stopAllWater(svg)
      }
    } else {
      return !state;
    }
  } else {
    return !state;
  }
  return state;
}

function toggleValve(inputState, animationID) {
  console.log("animationID: " + animationID);
  console.log("inputState: " + inputState);
  var svg = document.getElementById("embedded-diagram").contentDocument;
  if (svg != null) {
    var svganim = svg.getElementById(animationID);
    if (svganim != null) {
      valveStates[animationID] = inputState;
      if (inputState) {
        svganim.setAttributeNS(null, "from", 0);
        svganim.setAttributeNS(null, "to", 9);
      } else {
        svganim.setAttributeNS(null, "from", 9);
        svganim.setAttributeNS(null, "to", 0);
      }
      svganim.beginElement();
      //TODO: Find a way to check the state of the pump
      checkWaterFlow(svg, isPumpRunning());
    } else {
      console.log("v1 experiment, svganim null");
      return !inputState;
    }
  } else {
    console.log("v1 experiment, svg null");
    return !inputState;
  }
  return inputState;
}

function initWaterFeedMotion() {
  var svg = document.getElementById("embedded-diagram").contentDocument;
  if (svg == null) {
    console.log("Failed to initialize waterFeedMotion");
    return false;
  }
  var water = svg.getElementById("waterFeedMotion");
  water.beginElement();
  var water = svg.getElementById("waterFeed");
  console.log("waterFeedMotion successfully initialized");
  water.pauseAnimations();
  return true;  
}

function initSecWaterMotion() {
  var svg = document.getElementById("embedded-diagram").contentDocument;
  if (svg == null) {
    console.log("Failed to initialize secWater");
    return false;
  }
  var water = svg.getElementById("secWaterMotion");
  water.beginElement();
  var water = svg.getElementById("secWater");
  console.log("secWater successfully initialized");
  water.pauseAnimations();
  return true;  
}

function initMainWaterDown() {
  var svg = document.getElementById("embedded-diagram").contentDocument;
  if (svg == null) {
    console.log("Failed to initialize MainWaterDown");
    return false;
  }
  var water = svg.getElementById("mainWaterDown");
  water.beginElement();
  var water = svg.getElementById("wmDown");
  console.log("MainWaterDown successfully initialized");
  water.pauseAnimations();
  return true;  
}

function initMainWaterTop() {
  var svg = document.getElementById("embedded-diagram").contentDocument;
  if (svg == null) {
    console.log("Failed to initialize mwTop");
    return false;
  }
  var water = svg.getElementById("mainWaterTop");
  water.beginElement();
  var water = svg.getElementById("mwTop");
  console.log("mwTop successfully initialized");
  water.pauseAnimations();
  return true;
}

function initWaterMainValveInlet() {
  var svg = document.getElementById("embedded-diagram").contentDocument;
  if (svg == null) {
    console.log("Failed to initialize mainValveInlet");
    return false;
  }
  var water = svg.getElementById("mainValveInlet");
  water.beginElement();
  var water = svg.getElementById("mainValveInletWater");
  console.log("mainValveInlet successfully initialized");
  water.pauseAnimations();
  return true;
}

function initWaterMainValveExitAnimation() {
  var svg = document.getElementById("embedded-diagram").contentDocument;
  if (svg == null) {
    console.log("Failed to initialize mainValveExitWater");
    return false;
  }
  var water = svg.getElementById("mainValveExit");
  water.beginElement();
  var water = svg.getElementById("mainValveExitWater");
  console.log("mainValveExitWater successfully initialized");
  water.pauseAnimations();
  return true;
}

function initDirtWaterAnimation() {
  var svg = document.getElementById("embedded-diagram").contentDocument;
  if (svg == null) {
    console.log("Failed to initialize dirtWaterAnimation");
    return false;
  }
  var water = svg.getElementById("dirtWaterAnimation");
  water.beginElement();
  var water = svg.getElementById("dirtWater");
  console.log("DirtWaterAnimation successfully initialized");
  water.pauseAnimations();
  return true;
}

function initPumpAnimation() {
  var svg = document.getElementById("embedded-diagram").contentDocument;
  if (svg == null) {
    console.log("Failed to initialize pumpAnimation");
    return false;
  }
  var pump = svg.getElementById("pumpImpellerAnimation");
  pump.beginElement();
  svg.getElementById("pumpImpeller").pauseAnimations();
  console.log("PumpAnimation successfully initialized");
  return true;
}

function lazyTrigger(someFunc, ms, maxRetries) {
  setTimeout(() => {
    retryCount = 0;
    while (someFunc() && retryCount < maxRetries)
      retryCount++;
  }, ms)
}

function isPumpRunning() {
  var svg = document.getElementById("embedded-diagram").contentDocument;
  if (svg == null) {
    console.log("Failed to find svg component");
    return false;
  }

  var pumpAnimation = svg.getElementById("pumpImpeller");
  if (pumpAnimation != null) {
    return !pumpAnimation.animationsPaused();
  }
  console.log("Failed to find pumpAnimation component");
  return;
}

function stopAllWater(svg) {
  let water = svg.getElementById("dirtWater");
  water.pauseAnimations();
  water = svg.getElementById("waterFeed");
  water.pauseAnimations();
  water = svg.getElementById("secWater");
  water.pauseAnimations();
  water = svg.getElementById("mainValveInletWater");
  water.pauseAnimations();
  water = svg.getElementById("mainValveExitWater");
  water.pauseAnimations();
  water = svg.getElementById("mwTop");
  water.pauseAnimations();
  water = svg.getElementById("wmDown");
  water.pauseAnimations();
  return;
}

function checkWaterFlow(svg, pumpState) {
  if (svg == null) {
    return;
  }
  console.log("pumpState: " + pumpState);
  if (pumpState) {
    systemValves.forEach((valveId) => {
      if (valveStates[valveId]) {
        if (valveId == "valve1") {
          //Water flow for valve 1
          let water = svg.getElementById("dirtWater");
          water.unpauseAnimations();
        } else if (valveId == "valve2") {
          //Water flow for valve 2
          let water = svg.getElementById("waterFeed");
          water.unpauseAnimations();
          water = svg.getElementById("mainValveInletWater");
          water.unpauseAnimations();
          water = svg.getElementById("mainValveExitWater");
          water.unpauseAnimations();
          water = svg.getElementById("mwTop");
          water.unpauseAnimations();
          water = svg.getElementById("wmDown");
          water.unpauseAnimations();
        } else if (valveId == "valve3") {
          //Water flow for valve 3
          let water = svg.getElementById("waterFeed");
          water.unpauseAnimations();
          water = svg.getElementById("secWater");
          water.unpauseAnimations();
        } else {
          console.log("Oh, thats not suppose to happen!");
        }
      } else {
        if (valveId == "valve1") {
          //Stop flow through valve 1
          let water = svg.getElementById("dirtWater");
          water.pauseAnimations();
        } else if (valveId == "valve2") {
          //Stop flow through valve 2
          if (!valveStates["valve3"]) {
            let water = svg.getElementById("waterFeed");
            water.pauseAnimations();
          }
          let water = svg.getElementById("mainValveInletWater");
          water.pauseAnimations();
          water = svg.getElementById("mainValveExitWater");
          water.pauseAnimations();
          water = svg.getElementById("mwTop");
          water.pauseAnimations();
          water = svg.getElementById("wmDown");
          water.pauseAnimations();
        } else if (valveId == "valve3") {
          //Stop flow through valve 3
          if (!valveStates["valve2"]) {
            let water = svg.getElementById("waterFeed");
            water.pauseAnimations();
          }
          let water = svg.getElementById("secWater");
          water.pauseAnimations();
        } else {
          console.log("Why, thats hella weird!");
        }
      }
    });
    return;
  } else {
    console.log("Flow stopped!");
    stopAllWater(svg);
  }
}


