const { createApp } = Vue;

createApp({
  data() {
    return {
      email: '',
      password: '',
      regUsername: '',
      regEmail: '',
      regPassword: '',
      loading: false,
      message: '',
      isError: false,
      showRegister: false
    };
  },
  methods: {
    async login() {
      this.resetFeedback();
      this.loading = true;

      try {
        const res = await fetch('/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: this.email, password: this.password })
        });

        const data = await res.json();

        if (res.ok) {
          const token = data.response.user.authentication_token;
          localStorage.setItem('token', token);

          const roles = data.response.user.roles;
          window.location.href = roles.includes('admin')
            ? 'admin_dashboard.html'
            : 'user_dashboard.html';
        } else {
          this.isError = true;
          this.message = data.message || 'Login failed';
        }
      } catch (err) {
        this.isError = true;
        this.message = 'Error connecting to server.';
      } finally {
        this.loading = false;
      }
    },

    async register() {
      this.resetFeedback();
      this.loading = true;

      try {
        const res = await fetch('/api/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: this.regEmail,
            username: this.regUsername,
            password: this.regPassword
          })
        });

        const result = await res.json();

        if (res.ok) {
          this.message = result.message || 'Registration successful!';
          this.isError = false;
          this.showRegister = false;
        } else {
          this.message = result.message || 'Registration failed';
          this.isError = true;
        }
      } catch (err) {
        this.isError = true;
        this.message = 'Error connecting to server.';
      } finally {
        this.loading = false;
      }
    },

    resetFeedback() {
      this.message = '';
      this.isError = false;
    }
  }
}).mount('#app');
