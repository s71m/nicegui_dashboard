function createResizer() {
    const resizer = document.createElement('div');
    resizer.className = 'drawer-resizer';
    return resizer;
}

function updateDrawerWidth(newWidth) {
    const parentDrawer = document.querySelector('.q-drawer');
    if (parentDrawer) {
        parentDrawer.style.width = `${newWidth}px`;
        // Store the current width in a data attribute
        parentDrawer.setAttribute('data-drawer-width', newWidth);
    }
}

function setupDrawerResize() {
    const drawer = document.querySelector('.nicegui-drawer');
    if (!drawer) return;

    drawer.style.position = 'relative';

    const resizer = createResizer();
    drawer.appendChild(resizer);

    let isResizing = false;

    resizer.onmousedown = (e) => {
        isResizing = true;
        const startX = e.pageX;
        const startWidth = parseInt(getComputedStyle(drawer.parentElement).width);

        const onMouseMove = (e) => {
            if (!isResizing) return;
            const newWidth = startWidth + e.pageX - startX;
            updateDrawerWidth(newWidth);
            const page = document.querySelector('.q-page-container');
            if (page) {
                page.style.paddingLeft = `${newWidth}px`;
            }
        };

        const onMouseUp = () => {
            isResizing = false;
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    };
}

document.addEventListener('DOMContentLoaded', () => {
    const drawer = document.querySelector('.q-drawer');
    if (!drawer) return;

    setupDrawerResize();

    // Read the saved width from the data attribute or use default

    const savedWidth = drawer.getAttribute('data-drawer-width');
    if (savedWidth) {
        drawerWidth = parseInt(savedWidth);
    } else {
        const computedWidth = parseInt(getComputedStyle(drawer).width);
        if (computedWidth) {
            drawerWidth = computedWidth;
        }
    }
    updateDrawerWidth(drawerWidth);

    const page = document.querySelector('.q-page-container');
    if (page) {
        // Check if the drawer is currently closed
        const isClosed = drawer.classList.contains('q-layout--prevent-focus');
        page.style.paddingLeft = isClosed ? '0px' : `${drawerWidth}px`;
    }

    drawer.addEventListener('transitionend', () => {
        const isClosed = drawer.classList.contains('q-layout--prevent-focus');
        const savedWidth = drawer.getAttribute('data-drawer-width');
        if (savedWidth) {
            drawerWidth = parseInt(savedWidth);
        } else {
            const computedWidth = parseInt(getComputedStyle(drawer).width);
            if (computedWidth) {
                drawerWidth = computedWidth;
            }
        }
        if (!isClosed) {
            updateDrawerWidth(drawerWidth);
        }
        const page = document.querySelector('.q-page-container');
        if (page) {
            page.style.paddingLeft = isClosed ? '0px' : `${drawerWidth}px`;
        }
    });
});
