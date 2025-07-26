import Home from '../components/Home.js';
import Login from './components/Login.js';
import Register from '/components/Register.js';
import Navbar from '/components/Navbar.js';
import Foot from '/components/Footer.js';

const { createRouter, createWebHistory } = VueRouter;

const routes = [
    { path: '/', component: Home },
    { path: '/login', component: Login },
    { path: '/register', component: Register }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

const app = Vue.createApp({
    template: `
        <div class="container">
            <nav-bar></nav-bar>
            <router-view></router-view>
            <foot></foot>
        </div>
    `,
    components: {
        'nav-bar': Navbar,
        'foot': Foot
    }
});

// Use the router
app.use(router);

// Mount the app
app.mount('#app');
