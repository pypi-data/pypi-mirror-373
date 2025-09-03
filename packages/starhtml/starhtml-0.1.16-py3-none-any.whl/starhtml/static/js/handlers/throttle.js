function createDynamicThrottle() {
  let timeoutId = null;
  let lastExecTime = 0;
  return (func, delay = 150) => {
    const currentTime = Date.now();
    const timeSinceLastExec = currentTime - lastExecTime;
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    if (timeSinceLastExec >= delay) {
      func();
      lastExecTime = currentTime;
    } else {
      const remainingDelay = delay - timeSinceLastExec;
      timeoutId = setTimeout(() => {
        func();
        lastExecTime = Date.now();
        timeoutId = null;
      }, remainingDelay);
    }
  };
}
function createRAFThrottle(func) {
  let rafId = null;
  return function(...args) {
    if (rafId !== null) return;
    rafId = requestAnimationFrame(() => {
      try {
        func.apply(this, args);
      } finally {
        rafId = null;
      }
    });
  };
}
function createTimerThrottle(func, delay) {
  let timeoutId;
  let lastExecTime = 0;
  return function(...args) {
    const currentTime = Date.now();
    if (currentTime - lastExecTime > delay) {
      func.apply(this, args);
      lastExecTime = currentTime;
    } else {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(
        () => {
          func.apply(this, args);
          lastExecTime = Date.now();
        },
        delay - (currentTime - lastExecTime)
      );
    }
  };
}
function createElementThrottle() {
  const throttleConfigs = /* @__PURE__ */ new WeakMap();
  return (element, func, delay = 150) => {
    let config = throttleConfigs.get(element);
    if (!config) {
      config = { lastExec: 0, timeoutId: null };
      throttleConfigs.set(element, config);
    }
    const now = Date.now();
    const timeSinceLastExec = now - config.lastExec;
    if (config.timeoutId) {
      clearTimeout(config.timeoutId);
      config.timeoutId = null;
    }
    if (timeSinceLastExec >= delay) {
      config.lastExec = now;
      return func.call(element);
    }
    const remainingDelay = delay - timeSinceLastExec;
    config.timeoutId = setTimeout(() => {
      config.lastExec = Date.now();
      config.timeoutId = null;
      func.call(element);
    }, remainingDelay);
  };
}
function createDebounce(func, delay) {
  let timeoutId = null;
  return function(...args) {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    timeoutId = setTimeout(() => {
      func.apply(this, args);
      timeoutId = null;
    }, delay);
  };
}
export {
  createDebounce,
  createDynamicThrottle,
  createElementThrottle,
  createRAFThrottle,
  createTimerThrottle
};
