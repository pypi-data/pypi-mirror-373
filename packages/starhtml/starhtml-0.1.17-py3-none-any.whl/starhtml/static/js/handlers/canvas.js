function parseConfig(config) {
  return {
    signal: config?.signal || "canvas",
    enablePan: config?.enablePan !== false,
    enableZoom: config?.enableZoom !== false,
    minZoom: config?.minZoom || 0.01,
    maxZoom: config?.maxZoom || 100,
    touchEnabled: config?.touchEnabled !== false,
    contextMenuEnabled: config?.contextMenuEnabled !== false,
    spacebarPan: config?.spacebarPan !== false,
    middleClickPan: config?.middleClickPan !== false
  };
}
const ZOOM_FACTOR = 1.2;
const WHEEL_ZOOM_IN = 1.05;
const WHEEL_ZOOM_OUT = 0.95;
class CanvasController {
  constructor(ctx, config) {
    this.ctx = ctx;
    this.camera = { x: 0, y: 0, z: 1 };
    this.viewport = null;
    this.container = null;
    this.gestureState = {
      pointers: /* @__PURE__ */ new Map(),
      isGesturing: false,
      mode: "none"
    };
    this.isPanning = false;
    this.lastPanPoint = null;
    this.isSpacePressed = false;
    this.rafId = null;
    this.needsRender = false;
    this.lastViewportWidth = 0;
    this.lastViewportHeight = 0;
    this.resizeObserver = null;
    this.boundHandlePointerDown = this.handlePointerDown.bind(this);
    this.boundHandleWheel = this.handleWheel.bind(this);
    this.boundHandleKeyDown = this.handleKeyDown.bind(this);
    this.boundHandleKeyUp = this.handleKeyUp.bind(this);
    this.boundHandleContextMenu = this.handleContextMenu.bind(this);
    this.boundHandlePointerMove = this.handlePointerMove.bind(this);
    this.boundHandlePointerUp = this.handlePointerUp.bind(this);
    this.config = config;
    this.setupEventListeners();
    this.initializeDOMElements();
    this.startRenderLoop();
  }
  setupEventListeners() {
    document.addEventListener("pointerdown", this.boundHandlePointerDown);
    document.addEventListener("wheel", this.boundHandleWheel, { passive: false });
    if (this.config.spacebarPan) {
      document.addEventListener("keydown", this.boundHandleKeyDown);
      document.addEventListener("keyup", this.boundHandleKeyUp);
    }
    if (this.config.contextMenuEnabled) {
      document.addEventListener("contextmenu", this.boundHandleContextMenu);
    }
  }
  initializeDOMElements() {
    requestAnimationFrame(() => {
      this.viewport = document.querySelector("[data-canvas-viewport]");
      this.container = document.querySelector("[data-canvas-container]");
      if (this.viewport) {
        this.setupViewportStyles();
        this.setupResizeObserver();
        this.centerCanvas();
      }
      this.scheduleRender();
    });
  }
  centerCanvas() {
    if (!this.viewport) return;
    const rect = this.viewport.getBoundingClientRect();
    const viewportWidth = rect.width;
    const viewportHeight = rect.height;
    this.camera.x = viewportWidth / 2 / this.camera.z;
    this.camera.y = viewportHeight / 2 / this.camera.z;
  }
  setupResizeObserver() {
    if (!this.viewport) return;
    const rect = this.viewport.getBoundingClientRect();
    this.lastViewportWidth = rect.width;
    this.lastViewportHeight = rect.height;
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        this.handleViewportResize(entry.contentRect);
      }
    });
    resizeObserver.observe(this.viewport);
    this.resizeObserver = resizeObserver;
  }
  handleViewportResize(rect) {
    const newWidth = rect.width;
    const newHeight = rect.height;
    if (newWidth === this.lastViewportWidth && newHeight === this.lastViewportHeight) {
      return;
    }
    if (newWidth === 0 || newHeight === 0) {
      return;
    }
    const oldCenterX = this.lastViewportWidth / 2;
    const oldCenterY = this.lastViewportHeight / 2;
    const worldCenterX = oldCenterX / this.camera.z - this.camera.x;
    const worldCenterY = oldCenterY / this.camera.z - this.camera.y;
    const newCenterX = newWidth / 2;
    const newCenterY = newHeight / 2;
    this.camera.x = newCenterX / this.camera.z - worldCenterX;
    this.camera.y = newCenterY / this.camera.z - worldCenterY;
    this.lastViewportWidth = newWidth;
    this.lastViewportHeight = newHeight;
    this.scheduleRender();
  }
  setupViewportStyles() {
    if (!this.viewport) return;
    Object.assign(this.viewport.style, {
      userSelect: "none",
      webkitUserSelect: "none",
      touchAction: "none",
      cursor: "grab",
      willChange: "transform",
      ...window.devicePixelRatio > 1 && { imageRendering: "pixelated" }
    });
  }
  handlePointerDown(evt) {
    const target = evt.target;
    const draggableElement = target.closest("[data-draggable]");
    if (draggableElement) {
      return;
    }
    const viewport = target.closest("[data-canvas-viewport]");
    if (!viewport || !this.config.enablePan) return;
    this.viewport = viewport;
    this.gestureState.pointers.set(evt.pointerId, evt);
    const pointerCount = this.gestureState.pointers.size;
    if (pointerCount === 1) {
      this.handleSinglePointerDown(evt);
    } else if (pointerCount === 2) {
      this.handleMultiTouchStart();
    }
  }
  handleSinglePointerDown(evt) {
    const isLeftClick = evt.button === 0;
    const isMiddleClick = evt.button === 1 && this.config.middleClickPan;
    const isSpacePan = this.isSpacePressed && isLeftClick;
    if (!isLeftClick && !isMiddleClick && !isSpacePan) return;
    evt.preventDefault();
    this.startPanning(evt);
  }
  handleMultiTouchStart() {
    if (!this.config.touchEnabled) return;
    const pointers = Array.from(this.gestureState.pointers.values());
    if (pointers.length !== 2) return;
    this.gestureState.mode = "pinch";
    this.gestureState.isGesturing = true;
    this.gestureState.initialDistance = this.getDistance(pointers[0], pointers[1]);
    this.gestureState.initialCenter = this.getCenter(pointers[0], pointers[1]);
    this.gestureState.initialCamera = { ...this.camera };
    if (this.viewport) {
      const rect = this.viewport.getBoundingClientRect();
      const screenPoint = {
        x: this.gestureState.initialCenter.x - rect.left,
        y: this.gestureState.initialCenter.y - rect.top
      };
      this.gestureState.fixedWorldPoint = this.screenToCanvas(screenPoint);
    }
    this.stopPanning();
  }
  startPanning(evt) {
    this.isPanning = true;
    this.gestureState.mode = "pan";
    this.lastPanPoint = { x: evt.clientX, y: evt.clientY };
    if (this.viewport) {
      this.viewport.style.cursor = "grabbing";
    }
    document.addEventListener("pointermove", this.boundHandlePointerMove);
    document.addEventListener("pointerup", this.boundHandlePointerUp);
    document.addEventListener("pointercancel", this.boundHandlePointerUp);
  }
  stopPanning() {
    this.isPanning = false;
    this.lastPanPoint = null;
    if (this.viewport) {
      this.viewport.style.cursor = "grab";
    }
    document.removeEventListener("pointermove", this.boundHandlePointerMove);
    document.removeEventListener("pointerup", this.boundHandlePointerUp);
    document.removeEventListener("pointercancel", this.boundHandlePointerUp);
  }
  handlePointerMove(evt) {
    this.gestureState.pointers.set(evt.pointerId, evt);
    if (this.gestureState.mode === "pan" && this.isPanning) {
      this.handlePanMove(evt);
    } else if (this.gestureState.mode === "pinch" && this.gestureState.pointers.size === 2) {
      this.handlePinchMove();
    }
  }
  handlePanMove(evt) {
    if (!this.lastPanPoint) return;
    const deltaX = evt.clientX - this.lastPanPoint.x;
    const deltaY = evt.clientY - this.lastPanPoint.y;
    this.camera.x += deltaX / this.camera.z;
    this.camera.y += deltaY / this.camera.z;
    this.lastPanPoint = { x: evt.clientX, y: evt.clientY };
    this.scheduleRender();
  }
  handlePinchMove() {
    const pointers = Array.from(this.gestureState.pointers.values());
    if (pointers.length !== 2) return;
    const currentDistance = this.getDistance(pointers[0], pointers[1]);
    const currentCenter = this.getCenter(pointers[0], pointers[1]);
    if (this.gestureState.initialDistance && this.gestureState.initialCamera && this.viewport) {
      const scaleFactor = currentDistance / this.gestureState.initialDistance;
      const targetZoom = this.clampZoom(this.gestureState.initialCamera.z * scaleFactor);
      const rect = this.viewport.getBoundingClientRect();
      const pinchScreenX = currentCenter.x - rect.left;
      const pinchScreenY = currentCenter.y - rect.top;
      if (targetZoom !== this.camera.z) {
        this.zoomAtPoint(pinchScreenX, pinchScreenY, targetZoom / this.camera.z);
      }
    }
  }
  handlePointerUp(evt) {
    this.gestureState.pointers.delete(evt.pointerId);
    if (this.gestureState.pointers.size === 0) {
      this.gestureState.mode = "none";
      this.gestureState.isGesturing = false;
      this.stopPanning();
    } else if (this.gestureState.pointers.size === 1 && this.gestureState.mode === "pinch") {
      const remainingPointer = Array.from(this.gestureState.pointers.values())[0];
      this.startPanning(remainingPointer);
    }
  }
  handleWheel(evt) {
    const target = evt.target;
    const viewport = target.closest("[data-canvas-viewport]");
    if (!viewport || !this.config.enableZoom) return;
    evt.preventDefault();
    const rect = viewport.getBoundingClientRect();
    const mouseX = evt.clientX - rect.left;
    const mouseY = evt.clientY - rect.top;
    const zoomFactor = evt.deltaY > 0 ? WHEEL_ZOOM_OUT : WHEEL_ZOOM_IN;
    this.zoomAtPoint(mouseX, mouseY, zoomFactor);
  }
  handleKeyDown(evt) {
    if (evt.code === "Space" && this.config.spacebarPan) {
      evt.preventDefault();
      if (!this.isSpacePressed) {
        this.isSpacePressed = true;
        if (this.viewport) {
          this.viewport.style.cursor = "grab";
        }
      }
    }
    if ((evt.ctrlKey || evt.metaKey) && this.config.enableZoom) {
      const zoomActions = {
        "=": () => this.zoomAtCenter(ZOOM_FACTOR),
        "+": () => this.zoomAtCenter(ZOOM_FACTOR),
        "-": () => this.zoomAtCenter(1 / ZOOM_FACTOR),
        "0": () => this.resetView()
      };
      const action = zoomActions[evt.key];
      if (action) {
        action();
        evt.preventDefault();
      }
    }
  }
  handleKeyUp(evt) {
    if (evt.code === "Space" && this.config.spacebarPan) {
      evt.preventDefault();
      this.isSpacePressed = false;
      if (this.viewport && !this.isPanning) {
        this.viewport.style.cursor = "grab";
      }
    }
  }
  handleContextMenu(evt) {
    const target = evt.target;
    const viewport = target.closest("[data-canvas-viewport]");
    if (!viewport) return;
    evt.preventDefault();
    const rect = viewport.getBoundingClientRect();
    const canvasPoint = this.screenToCanvas({
      x: evt.clientX - rect.left,
      y: evt.clientY - rect.top
    });
    this.ctx.mergePatch({
      [`${this.config.signal}_context_menu_x`]: canvasPoint.x,
      [`${this.config.signal}_context_menu_y`]: canvasPoint.y,
      [`${this.config.signal}_context_menu_screen_x`]: evt.clientX,
      [`${this.config.signal}_context_menu_screen_y`]: evt.clientY
    });
  }
  clampZoom(zoom) {
    return Math.max(this.config.minZoom, Math.min(this.config.maxZoom, zoom));
  }
  zoomAtPoint(screenX, screenY, zoomFactor) {
    const oldZoom = this.camera.z;
    const newZoom = this.clampZoom(oldZoom * zoomFactor);
    if (newZoom !== oldZoom) {
      const worldX = screenX / oldZoom - this.camera.x;
      const worldY = screenY / oldZoom - this.camera.y;
      this.camera.z = newZoom;
      this.camera.x = screenX / newZoom - worldX;
      this.camera.y = screenY / newZoom - worldY;
      this.scheduleRender();
    }
  }
  zoomAtCenter(zoomFactor) {
    if (!this.viewport) return;
    const rect = this.viewport.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    this.zoomAtPoint(centerX, centerY, zoomFactor);
  }
  resetView() {
    this.camera.z = 1;
    this.centerCanvas();
    this.scheduleRender();
  }
  zoomIn() {
    this.zoomAtCenter(ZOOM_FACTOR);
  }
  zoomOut() {
    this.zoomAtCenter(1 / ZOOM_FACTOR);
  }
  screenToCanvas(point) {
    return {
      x: point.x / this.camera.z - this.camera.x,
      y: point.y / this.camera.z - this.camera.y
    };
  }
  canvasToScreen(point) {
    return {
      x: (point.x + this.camera.x) * this.camera.z,
      y: (point.y + this.camera.y) * this.camera.z
    };
  }
  getDistance(pointer1, pointer2) {
    return Math.sqrt(
      (pointer2.clientX - pointer1.clientX) ** 2 + (pointer2.clientY - pointer1.clientY) ** 2
    );
  }
  getCenter(pointer1, pointer2) {
    return {
      x: (pointer1.clientX + pointer2.clientX) / 2,
      y: (pointer1.clientY + pointer2.clientY) / 2
    };
  }
  startRenderLoop() {
    const render = () => {
      if (this.needsRender) {
        this.updateTransform();
        this.updateSignals();
        this.needsRender = false;
      }
      this.rafId = requestAnimationFrame(render);
    };
    this.rafId = requestAnimationFrame(render);
  }
  scheduleRender() {
    this.needsRender = true;
  }
  updateTransform() {
    if (!this.container) return;
    const transform = `translate(${this.camera.x * this.camera.z}px, ${this.camera.y * this.camera.z}px) scale(${this.camera.z})`;
    this.container.style.transform = transform;
    this.container.style.transformOrigin = "0 0";
  }
  updateSignals() {
    this.ctx.startBatch();
    try {
      this.ctx.mergePatch({
        [`${this.config.signal}_pan_x`]: this.camera.x,
        [`${this.config.signal}_pan_y`]: this.camera.y,
        [`${this.config.signal}_zoom`]: this.camera.z,
        [`${this.config.signal}_is_panning`]: this.isPanning,
        [`${this.config.signal}_reset_view`]: this.resetView.bind(this),
        [`${this.config.signal}_zoom_in`]: this.zoomIn.bind(this),
        [`${this.config.signal}_zoom_out`]: this.zoomOut.bind(this)
      });
      this.ctx.rx(this.camera.x, this.camera.y, this.camera.z, this.isPanning);
    } catch (error) {
      console.error("Error executing canvas handler:", error);
    } finally {
      this.ctx.endBatch();
    }
  }
  destroy() {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
    }
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
    document.removeEventListener("pointerdown", this.boundHandlePointerDown);
    document.removeEventListener("wheel", this.boundHandleWheel);
    document.removeEventListener("keydown", this.boundHandleKeyDown);
    document.removeEventListener("keyup", this.boundHandleKeyUp);
    document.removeEventListener("contextmenu", this.boundHandleContextMenu);
    this.stopPanning();
  }
}
const canvasAttributePlugin = {
  type: "attribute",
  name: "onCanvas",
  keyReq: "starts",
  onLoad(ctx) {
    const { value } = ctx;
    if (!value) return;
    const globalConfig = window.__starhtml_canvas_config;
    const config = parseConfig(globalConfig);
    const controller = new CanvasController(ctx, config);
    return () => {
      controller.destroy();
    };
  }
};
const canvasPlugin = {
  ...canvasAttributePlugin,
  setConfig(config) {
    window.__starhtml_canvas_config = config;
  }
};
var canvas_default = canvasPlugin;
export {
  canvas_default as default
};
