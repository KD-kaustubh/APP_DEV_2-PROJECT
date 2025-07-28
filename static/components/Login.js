export default {
  name: 'LoginPage',
  template: `
    <div class="container login-container shadow p-4 bg-white rounded mt-5" style="max-width: 400px;">
      <h2 class="text-center mb-4">Login</h2>
      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label for="email" class="form-label">Email address</label>
          <input 
            type="email" 
            v-model="email" 
            class="form-control" 
            id="email" 
            placeholder="Enter email" 
            required 
          />
        </div>
        <div class="mb-3 position-relative">
          <label for="password" class="form-label">Password</label>
          <input 
            :type="showPassword ? 'text' : 'password'" 
            v-model="password" 
            class="form-control" 
            id="password" 
            placeholder="Enter password" 
            required 
          />
          <span 
            @click="togglePassword" 
            style="position: absolute; right: 10px; top: 38px; cursor: pointer; user-select: none;" 
            title="Toggle password visibility"
          >
            <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
          </span>
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
      password: '',
      showPassword: false,
    };
  },
  methods: {
  togglePassword() {
    this.showPassword = !this.showPassword;
  },
  async handleLogin() {
    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: this.email,
          password: this.password,
        }),//backend pe data gaya
      });

      const data = await res.json();

      if (res.ok) {
        //token save in localstorage
        sessionStorage.setItem("auth_token", data.response.user.authentication_token);
        sessionStorage.setItem("user_email", data.response.user.email);
        sessionStorage.setItem("user_roles", JSON.stringify(data.response.user.roles));
        sessionStorage.setItem("user_uname", data.response.user.uname);
        // ------------------------------------

        alert(`Welcome back, ${data.response.user.email}!`);

        this.$router.push('/dashboard');  //yeh le jayega admin ya user par
      } 
      else {
        alert(data.message || 'Login failed');
      }
    } 
    catch (error) {
      alert('Error connecting to server.');
      console.error(error);
    }
  },
}
}
