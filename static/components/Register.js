export default {
  name: 'RegisterPage',
  template: `
    <div class="container register-container shadow p-4 bg-white rounded mt-5" style="max-width: 400px;">
      <h2 class="text-center mb-4">Register</h2>
      <form @submit.prevent="registerUser">
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
        <div class="mb-3">
          <label for="uname" class="form-label">Username</label>
          <input 
            type="text" 
            v-model="uname" 
            class="form-control" 
            id="uname" 
            placeholder="Choose a username" 
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
        <button type="submit" class="btn btn-primary w-100">Register</button>
      </form>

      <p class="text-center mt-3">
        Already have an account? <router-link to="/login">Login</router-link>
      </p>

      <div v-if="message" :class="{'text-success': success, 'text-danger': !success}" class="mt-3 text-center">
        {{ message }}
      </div>
    </div>
  `,
  data() {
    return {
      email: '',
      uname: '',
      password: '',
      showPassword: false,
      message: '',
      success: false,
    };
  },
  methods: {
    togglePassword() {
      this.showPassword = !this.showPassword;
    },
    async registerUser() {
      this.message = '';
      this.success = false;
      try {
        const res = await fetch('/api/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: this.email,
            uname: this.uname,
            password: this.password,
          }),
        });
        const data = await res.json();
        if (res.status === 201) {
          this.message = data.message;
          this.success = true;
          this.email = '';
          this.uname = '';
          this.password = '';
        } 
        else {
          this.message = data.message || 'Registration failed';
        }
      } 
      catch (error) {
        this.message = 'Error connecting to server.';
      }
    },
  },
};
