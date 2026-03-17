export default {
    template: `
    <section class="home-hero-wrap">
        <div class="card home-hero-card">
            <div class="card-body text-center p-4 p-md-5">
                <h1 class="display-6 fw-semibold mb-3">Vehicle Parking, Without the Guesswork</h1>
                <p class="lead mb-2">{{ message }}</p>
                <p class="text-muted mb-4">Trusted by daily commuters for fast booking, transparent billing, and reliable lot availability.</p>

                <div class="d-grid gap-2 d-sm-flex justify-content-sm-center mt-3 mb-4">
                    <router-link to="/login" class="btn btn-primary btn-lg">Login</router-link>
                    <router-link to="/register" class="btn btn-secondary btn-lg">Sign Up</router-link>
                </div>

                <div class="feature-badges">
                    <span class="feature-badge">Real-time availability</span>
                    <span class="feature-badge">Secure payment flow</span>
                    <span class="feature-badge">Quick reserve and release</span>
                </div>
            </div>
        </div>
    </section>
    `,
    data() {
        return {
            message: "Secure your parking spot in seconds with a clean, reliable booking flow.",
        };
    },
};
