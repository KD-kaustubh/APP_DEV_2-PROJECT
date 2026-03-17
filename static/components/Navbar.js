export default {
    name: 'Navbar',
    template: `
        <nav class="navbar navbar-expand-lg navbar-dark nav-glass fixed-top">
            <div class="container-fluid">
                <router-link class="navbar-brand fw-semibold d-flex align-items-center gap-2" to="/" @click="closeNavMenu">
                    <i class="bi bi-car-front-fill"></i>
                    <span>ParkingApp</span>
                </router-link>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>

                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto align-items-lg-center gap-lg-1">
                        <!-- Show Home ONLY if NOT logged in -->
                        <li v-if="!isLoggedIn" class="nav-item">
                            <router-link class="nav-link nav-pill" :class="{ active: $route.path === '/' }" to="/" @click="closeNavMenu">Home</router-link>
                        </li>

                        <!-- Show Login/Register ONLY if NOT logged in -->
                        <template v-if="!isLoggedIn">
                            <li class="nav-item">
                                <router-link class="nav-link nav-pill" :class="{ active: $route.path === '/login' }" to="/login" @click="closeNavMenu">Login</router-link>
                            </li>
                            <li class="nav-item">
                                <router-link class="nav-link nav-pill" :class="{ active: $route.path === '/register' }" to="/register" @click="closeNavMenu">Register</router-link>
                            </li>
                        </template>

                        <li v-if="isLoggedIn" class="nav-item me-lg-2 mt-2 mt-lg-0">
                            <span class="badge role-badge">{{ userRoleLabel }}</span>
                        </li>

                        <!-- Show Logout button ONLY if logged in -->
                        <li v-if="isLoggedIn" class="nav-item">
                            <a class="nav-link nav-pill" href="#" @click.prevent="logout" style="cursor: pointer;">Logout</a>
                        </li>

                    </ul>
                </div>
            </div>
        </nav>
    `,
    data() {
        return {
            isLoggedIn: false,
        };
    },
    methods: {
        closeNavMenu() {
            const menu = document.getElementById('navbarNav');
            if (!menu || !menu.classList.contains('show')) return;
            const instance = bootstrap.Collapse.getInstance(menu) || new bootstrap.Collapse(menu, { toggle: false });
            instance.hide();
        },
        logout() {
            // Remove all user data from sessionStorage
            sessionStorage.removeItem('auth_token');
            sessionStorage.removeItem('user_email');
            sessionStorage.removeItem('user_roles');
            this.updateLoginState();
            this.closeNavMenu();
            this.$router.replace('/login'); // Use replace for better UX
        },
        updateLoginState() {
            // The navbar is "logged in" if the auth_token exists in sessionStorage
            this.isLoggedIn = !!sessionStorage.getItem('auth_token');
        },
    },
    computed: {
        isAdmin() {
            const roles = JSON.parse(sessionStorage.getItem('user_roles') || '[]');
            return roles.includes('admin');
        },
        userRoleLabel() {
            return this.isAdmin ? 'Admin' : 'User';
        },
        isDashboard() {
            return this.$route.path === '/dashboard';
        }
    },
    mounted() {
        // Check login state when the component is first created
        this.updateLoginState();
    },
    watch: {
        // Watch for changes in the route (i.e., when user navigates)
        '$route'() {
            // Re-check the login state every time the page changes
            this.updateLoginState();
        }
    }
};
