function stayWithMe() {
    // a change of location (URL) returns sidebar
    location.href = "#/";
}

function sidebar() {
    // draw out the sidebar
    location.href = "#sw-sidebar";
    void(0);
}

function subMenu(menu_id) {
    var subs = document.getElementsByClassName("sw-submenu");
    for (i = 0; i < subs.length; i++) {
        subs[i].style.display = "none";
    }
    var menuitem = document.getElementById(menu_id);
    menuitem.style.display = "block";
}

const docpage = document.querySelector('main');
docpage.addEventListener('click', stayWithMe);
