export default {
    template: `
    <div class="container text-center mt-5">
        <h3 class="mb-4">🚗 Welcome to the Vehicle Parking App 🚗</h3>
        <p class="lead">DASHBOARD</p>
        <div v-if="userdata">
            <div>Email: {{ userdata.email }}</div>
            <div>Name: {{ userdata.uname }}</div>
        </div>
        <div class="d-flex justify-content-center gap-3 mt-4"></div>
    </div>
    `,
    data() {
        return {
            userdata: null
        };
    },
    mounted() {
        fetch('/api/home', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": localStorage.getItem("auth_token")
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            this.userdata = data.user; // Set userdata so it appears in the template
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

    }
}