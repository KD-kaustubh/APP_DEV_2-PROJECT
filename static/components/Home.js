export default {
    template: `
    <div class="container text-center mt-5">
        <h1 class="mb-4">🚗 Welcome to the Vehicle Parking App 🚗</h1>
        <p class="lead">{{ message }}</p>
        <div class="d-flex justify-content-center gap-3 mt-4">
            <router-link to="/login" class="btn btn-primary btn-lg">Login</router-link>
            <router-link to="/register" class="btn btn-primary btn-lg">Sign Up</router-link>
        </div>
    </div>
    `,
    data() {
        return {
            message: "Secure your parking spot with ease!",
        };
    },
};
