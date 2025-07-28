export default {
    template: `
    <div class="container mt-4">
        <h2>All Users</h2>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Current Spot</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="user in users" :key="user.id">
                    <td>{{ user.uname }}</td>
                    <td>{{ user.email }}</td>
                    <td>{{ user.current_spot || 'None' }}</td>
                    <td>{{ user.status }}</td>
                </tr>
            </tbody>
        </table>
    </div>
    `,
    data() {
        return {
            users: []
        };
    },
    async mounted() {
        try {
            const token = sessionStorage.getItem("auth_token");
            const res = await fetch('/api/admin/users', {
                headers: { 'Authentication-Token': token }
            });
            const data = await res.json();
            this.users = data.users;
        } catch (e) {
            alert("Failed to load users");
        }
    }
}