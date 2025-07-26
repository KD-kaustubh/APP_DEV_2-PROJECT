import Home from './components/home.js';
import Login from './components/Login.js';
import Register from './components/Register.js';
import Navbar from './components/Navbar.js';
import Foot from './components/Footer.js';

const { createRouter, createWebHashHistory } = VueRouter;

const routes = [
    { path: '/', component: Home },
    { path: '/login', component: Login },
    { path: '/register', component: Register }
];

const router = createRouter({
    history: createWebHashHistory(),
    routes: routes
});

const app = Vue.createApp({
    template: `
        <div class="container">
            <nav-bar></nav-bar>
            <router-view></router-view>
            <foot></foot>
        </div>
    `
});

app.component('nav-bar', Navbar);
app.component('foot', Foot);
app.use(router);
app.mount('#app');
