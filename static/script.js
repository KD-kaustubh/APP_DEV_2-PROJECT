import Home from './components/Home.js';
import Login from './components/Login.js';
import Register from './components/Register.js';
import Navbar from './components/Navbar.js';
import Foot from './components/Footer.js';
import Dashboard from './components/Dashboard.js';
import UsersList from './components/UsersList.js';

const { createRouter, createWebHashHistory } = VueRouter;

const routes = [
    { path: '/', component: Home },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/dashboard', component: Dashboard },
    { path: '/users', component: UsersList },
];

const router = createRouter({
    history: createWebHashHistory(),
    routes: routes
});

const app = Vue.createApp({
    template: `
        <div id="app">
            <nav-bar></nav-bar>
            <main>
                <router-view></router-view>
            </main>
            <foot></foot>
        </div>
    `
});




app.component('nav-bar', Navbar);
app.component('foot', Foot);
app.use(router);
app.mount('#app');
