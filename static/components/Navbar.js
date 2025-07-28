export default {
    name: 'Navbar',
    template: `
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
            <div class="container-fluid">
                <router-link class="navbar-brand" to="/">ParkingApp</router-link>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>

                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav ms-auto">
                        <!-- Show Home ONLY if NOT logged in -->
                        <li v-if="!isLoggedIn" class="nav-item">
                            <router-link class="nav-link" to="/">Home</router-link>
                        </li>

                        <!-- Show Login/Register ONLY if NOT logged in -->
                        <template v-if="!isLoggedIn">
                            <li class="nav-item">
                                <router-link class="nav-link" to="/login">Login</router-link>
                            </li>
                            <li class="nav-item">
                                <router-link class="nav-link" to="/register">Register</router-link>
                            </li>
                        </template>

                        <!-- Show Logout button ONLY if logged in -->
                        <li v-if="isLoggedIn" class="nav-item">
                            <a class="nav-link" href="#" @click.prevent="logout" style="cursor: pointer;">Logout</a>
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
        logout() {
            // Remove all user data from sessionStorage
            sessionStorage.removeItem('auth_token');
            sessionStorage.removeItem('user_email');
            sessionStorage.removeItem('user_roles');
            this.updateLoginState();
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
