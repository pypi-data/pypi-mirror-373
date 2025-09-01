const DEFAULT_SMOOTH_FACTOR = 0.1;
const DEFAULT_UPDATE_THRESHOLD = 0.1;
const smoothScrollStore = /* @__PURE__ */ new WeakMap();
function lerp(start, end, factor) {
  return start + (end - start) * factor;
}
class SmoothScroll {
  constructor(element, updateCallback, config = {}) {
    this.rafId = null;
    this.isActive = false;
    this.element = element;
    this.updateCallback = updateCallback;
    this.config = {
      factor: config.factor ?? DEFAULT_SMOOTH_FACTOR,
      threshold: config.threshold ?? DEFAULT_UPDATE_THRESHOLD
    };
  }
  getSmoothData(rawData) {
    let smoothData = smoothScrollStore.get(this.element);
    if (!smoothData) {
      smoothData = { ...rawData };
      smoothScrollStore.set(this.element, smoothData);
    }
    const needsUpdate = this.checkNeedsUpdate(smoothData, rawData);
    if (needsUpdate) {
      smoothData.scrollY = lerp(smoothData.scrollY, rawData.scrollY, this.config.factor);
      smoothData.velocity = lerp(smoothData.velocity, rawData.velocity, this.config.factor);
      smoothData.progress = lerp(smoothData.progress, rawData.progress, this.config.factor);
      smoothData.pageProgress = lerp(
        smoothData.pageProgress,
        rawData.pageProgress,
        this.config.factor
      );
      smoothData.visiblePercent = lerp(
        smoothData.visiblePercent,
        rawData.visiblePercent,
        this.config.factor
      );
      if (!this.rafId && this.isActive) {
        this.rafId = requestAnimationFrame(() => this.animationFrame());
      }
    }
    return smoothData;
  }
  checkNeedsUpdate(smoothData, rawData) {
    const threshold = this.config.threshold;
    return Math.abs(smoothData.scrollY - rawData.scrollY) > threshold || Math.abs(smoothData.velocity - rawData.velocity) > threshold || Math.abs(smoothData.progress - rawData.progress) > threshold || Math.abs(smoothData.pageProgress - rawData.pageProgress) > threshold || Math.abs(smoothData.visiblePercent - rawData.visiblePercent) > threshold;
  }
  animationFrame() {
    this.rafId = null;
    this.updateCallback();
  }
  start() {
    this.isActive = true;
  }
  stop() {
    this.isActive = false;
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }
  cleanup() {
    this.stop();
    smoothScrollStore.delete(this.element);
  }
}
export {
  SmoothScroll,
  lerp
};
