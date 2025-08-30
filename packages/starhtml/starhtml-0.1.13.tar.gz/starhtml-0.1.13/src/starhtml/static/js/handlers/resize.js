import { createDebounce, createTimerThrottle, createRAFThrottle } from "./throttle.js";
const DEFAULT_THROTTLE = 150;
const BREAKPOINT_THRESHOLDS = {
  xs: 640,
  sm: 768,
  md: 1024,
  lg: 1280,
  xl: 1536
};
const RESIZE_ARG_NAMES = [
  "width",
  "height",
  "windowWidth",
  "windowHeight",
  "aspectRatio",
  "isMobile",
  "isTablet",
  "isDesktop",
  "currentBreakpoint"
];
const hasResizeObserver = typeof ResizeObserver !== "undefined";
function parseTimingValue(value) {
  let actualValue = value;
  if (value instanceof Set) {
    actualValue = Array.from(value)[0];
  }
  const parsed = Number.parseInt(String(actualValue).replace("ms", ""));
  return Number.isNaN(parsed) ? DEFAULT_THROTTLE : parsed;
}
function parseModifiers(mods) {
  const debounceValue = mods.get("debounce");
  if (debounceValue !== void 0) {
    return { throttle: parseTimingValue(debounceValue), isDebounce: true };
  }
  const throttleValue = mods.get("throttle");
  if (throttleValue !== void 0) {
    return { throttle: parseTimingValue(throttleValue), isDebounce: false };
  }
  return { throttle: DEFAULT_THROTTLE, isDebounce: false };
}
function getBreakpoint(width) {
  if (width < BREAKPOINT_THRESHOLDS.xs) return "xs";
  if (width < BREAKPOINT_THRESHOLDS.sm) return "sm";
  if (width < BREAKPOINT_THRESHOLDS.md) return "md";
  if (width < BREAKPOINT_THRESHOLDS.lg) return "lg";
  if (width < BREAKPOINT_THRESHOLDS.xl) return "xl";
  return "2xl";
}
function createResizeContext(el, windowWidth, windowHeight) {
  const rect = el.getBoundingClientRect();
  const width = Math.round(rect.width);
  const height = Math.round(rect.height);
  return {
    width,
    height,
    windowWidth,
    windowHeight,
    aspectRatio: width > 0 ? Math.round(width / height * 100) / 100 : 0,
    isMobile: windowWidth < BREAKPOINT_THRESHOLDS.sm,
    isTablet: windowWidth >= BREAKPOINT_THRESHOLDS.sm && windowWidth < BREAKPOINT_THRESHOLDS.md,
    isDesktop: windowWidth >= BREAKPOINT_THRESHOLDS.md,
    currentBreakpoint: getBreakpoint(windowWidth)
  };
}
const resizeAttributePlugin = {
  type: "attribute",
  name: "onResize",
  keyReq: "starts",
  argNames: [...RESIZE_ARG_NAMES],
  onLoad(ctx) {
    const { el, value, mods, rx, mergePatch, startBatch, endBatch } = ctx;
    if (!value) {
      return;
    }
    const { throttle, isDebounce } = parseModifiers(mods);
    const handleResize = () => {
      const context = createResizeContext(el, window.innerWidth, window.innerHeight);
      startBatch();
      try {
        mergePatch(context);
        rx(
          context.width,
          context.height,
          context.windowWidth,
          context.windowHeight,
          context.aspectRatio,
          context.isMobile,
          context.isTablet,
          context.isDesktop,
          context.currentBreakpoint
        );
      } catch (error) {
        console.error("Error during resize handler:", error);
      } finally {
        endBatch();
      }
    };
    const throttledHandler = isDebounce ? createDebounce(handleResize, throttle) : throttle > 16 ? createTimerThrottle(handleResize, throttle) : createRAFThrottle(handleResize);
    let resizeObserver = null;
    if (hasResizeObserver) {
      resizeObserver = new ResizeObserver(() => throttledHandler());
      resizeObserver.observe(el);
    }
    const handleWindowResize = () => throttledHandler();
    window.addEventListener("resize", handleWindowResize, { passive: true });
    handleResize();
    return () => {
      resizeObserver?.disconnect();
      window.removeEventListener("resize", handleWindowResize);
    };
  }
};
let globalConfig = { debug: false };
const resizePlugin = {
  ...resizeAttributePlugin,
  setConfig(config) {
    globalConfig = { ...globalConfig, ...config };
  }
};
var resize_default = resizePlugin;
export {
  resize_default as default
};
