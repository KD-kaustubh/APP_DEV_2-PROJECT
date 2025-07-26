export default {
    name: 'LoginPage',
    template: `
        <div class="container login-container shadow p-4 bg-white rounded mt-5">
            <h2 class="text-center mb-4">Login</h2>
            <form @submit.prevent="handleLogin">
                <div class="mb-3">
                    <label for="email" class="form-label">Email address</label>
                    <input type="email" v-model="email" class="form-control" id="email" placeholder="Enter email" required>
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" v-model="password" class="form-control" id="password" placeholder="Enter password" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Login</button>
                <p class="text-center mt-3">
                    Don't have an account? <router-link to="/register">Register</router-link>
                </p>
            </form>
        </div>
    `,
    data() {
        return {
            email: '',
            password: ''
        };
    },
    methods: {
        handleLogin() {
            // Replace this with your actual login logic or API call
            console.log('ad c hai');
            console.log('Login attempted with', this.email, this.password);
            alert(`Login attempted:\nEmail: ${this.email}\nPassword: ${this.password}`);
        }
    }
};
