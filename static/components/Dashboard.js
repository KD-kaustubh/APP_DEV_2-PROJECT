export default {
    name: 'Dashboard',
    template: `
    <div class="container mt-4">
        <div v-if="loading" class="text-center">
            <div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>
        </div>

        <!-- #################### ADMIN DASHBOARD ######################## -->
        <div v-else-if="userRole === 'admin'">
            <h2 class="text-center mt-4 mb-2">Admin Dashboard</h2>
            <p class="text-center mb-4">Welcome</p>
            <div class="d-grid gap-2 d-md-flex justify-content-md-start mb-4">
                <button class="btn btn-primary" @click="showAddForm">Add New Parking Lot</button>
                <!-- Add this button to your admin dashboard button group -->
                <button class="btn btn-success" @click="showView = 'view_stats'; fetchAdminStats();">View Statistics</button>
            </div>
            <div>
                <!-- View 1: Show All Parking Lots Table -->
                <div v-if="showView === 'view_lots'">
                    <h3>All Parking Lots</h3>
                    <table class="table table-striped">
                        <thead><tr><th>Location</th><th>Price</th><th>Total Spots</th><th>Available</th><th>Actions</th></tr></thead>
                        <tbody>
                            <tr v-for="lot in lots" :key="lot.id">
                                <td>{{ lot.location }}</td>
                                <td>₹{{ lot.price.toFixed(2) }}</td>
                                <td>{{ lot.total_spots }}</td>
                                <td>{{ lot.available_spots }}</td>
                                <td>
                                    <button class="btn btn-sm btn-info me-2" @click="showEditForm(lot)">Edit</button>
                                    <button class="btn btn-sm btn-danger me-2" @click="deleteLot(lot.id)">Delete</button>
                                    <button class="btn btn-sm btn-secondary me-2" @click="showLotDetails(lot)">Details</button>
                                    <button class="btn btn-sm btn-warning" @click="viewSpots(lot)">View Spots</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- View 2: Add New Parking Lot Form -->
                <div v-if="showView === 'add_lot'">
                    <h3>Add a New Parking Lot</h3>
                    <div class="card p-4">
                         <div class="mb-3"><label class="form-label">Location Name</label><input type="text" class="form-control" v-model="newLot.location"></div>
                         <div class="mb-3"><label class="form-label">Price (per hour)</label><input type="number" class="form-control" v-model.number="newLot.price"></div>
                         <div class="mb-3"><label class="form-label">Address</label><input type="text" class="form-control" v-model="newLot.address"></div>
                         <div class="mb-3"><label class="form-label">Pin Code</label><input type="text" class="form-control" v-model="newLot.pin"></div>
                         <div class="mb-3"><label class="form-label">Number of Spots</label><input type="number" class="form-control" v-model.number="newLot.spots"></div>
                         <button class="btn btn-success me-2" @click="createLot">Create Lot</button>
                         <button class="btn btn-secondary" @click="cancelForm">Cancel</button>
                    </div>
                </div>

                <!-- View 3: Edit Existing Parking Lot Form -->
                <div v-if="showView === 'edit_lot'">
                    <h3>Edit Parking Lot</h3>
                    <div class="card p-4" v-if="editLotData">
                         <div class="mb-3"><label class="form-label">Location Name</label><input type="text" class="form-control" v-model="editLotData.location"></div>
                         <div class="mb-3"><label class="form-label">Price (per hour)</label><input type="number" class="form-control" v-model.number="editLotData.price"></div>
                         <div class="mb-3"><label class="form-label">Address</label><input type="text" class="form-control" v-model="editLotData.address"></div>
                         <div class="mb-3"><label class="form-label">Pin Code</label><input type="text" class="form-control" v-model="editLotData.pin"></div>
                         <div class="mb-3"><label class="form-label">Number of Spots</label><input type="number" class="form-control" v-model.number="editLotData.spots"></div>
                         <button class="btn btn-success me-2" @click="updateLot">Save Changes</button>
                         <button class="btn btn-secondary" @click="cancelForm">Cancel</button>
                    </div>
                </div>

                <!-- View 4: Parking Lot Details (Newly Added) -->
                <div v-if="selectedLot" class="card mt-3">
                    <div class="card-header">
                        <strong>Parking Lot Details</strong>
                        <button type="button" class="btn-close float-end" aria-label="Close" @click="selectedLot = null"></button>
                    </div>
                    <div class="card-body">
                        <p><strong>Location:</strong> {{ selectedLot.location }}</p>
                        <p><strong>Price:</strong> ₹{{ selectedLot.price.toFixed(2) }}</p>
                        <p><strong>Address:</strong> {{ selectedLot.address }}</p>
                        <p><strong>Pin Code:</strong> {{ selectedLot.pin }}</p>
                        <p><strong>Total Spots:</strong> {{ selectedLot.total_spots }}</p>
                        <p><strong>Available Spots:</strong> {{ selectedLot.available_spots }}</p>
                        <p><strong>Occupied Spots:</strong> {{ selectedLot.occupied_spots }}</p>
                    </div>
                </div>

                <!-- Add this section in your admin dashboard template -->
                <div v-if="showView === 'view_stats'">
                    <button class="btn btn-secondary mb-3" @click="showView = 'view_lots'">Close</button>
                    <h3>Parking & Revenue Statistics</h3>
                    <div class="row">
                        <div class="col-md-6">
                            <h4>Occupancy</h4>
                            <canvas id="occupancyChart"></canvas>
                        </div>
                        <div class="col-md-6">
                            <h4>Revenue by Lot</h4>
                            <canvas id="revenueChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- New Section: All Registered Users -->
                <div v-if="userRole === 'admin' && showView === 'view_lots'">
                    <h3 class="mt-5">All Registered Users</h3>
                    <table class="table table-bordered">
                        <thead>
                          <tr>
                            <th>#</th>
                            <th>Email</th>
                            <th>Name</th>
                            <th>Current Spot</th>
                            <th>Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="(user, index) in allUsers" :key="user.id">
                            <td>{{ index + 1 }}</td>
                            <td>{{ user.email }}</td>
                            <td>{{ user.uname }}</td>
                            <td>{{ user.current_spot || '-' }}</td>
                            <td>{{ user.status }}</td>
                          </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
        </div>


        <!-- #################### USER DASHBOARD #################### -->
        <div v-else>
             <h2 class="text-center mt-4 mb-2">User Dashboard</h2>
             <p class="text-center mb-4">Welcome, {{ userUname }}</p>

            <!-- User Action Buttons to switch views -->
             <div class="d-grid gap-2 d-md-flex justify-content-md-start mb-4">
                <button class="btn btn-primary" @click="showView = 'book_parking'">Book Parking & Reservations</button>
                <button class="btn btn-info" @click="showView = 'user_stats'; fetchUserStats();">View My Stats</button>
            </div>

            <!-- View: Booking and Reservations Table -->
            <div v-if="showView === 'book_parking'">
                <h3>My Reservations</h3>
                <div v-if="reservations.length === 0" class="alert alert-info">You have no past or active reservations.</div>
                <table v-else class="table">
                    <thead>
                      <tr>
                        <th>Status</th>
                        <th>Parking Lot</th>
                        <th>Vehicle</th>
                        <th>Parking Time</th>
                        <th>Release Time</th>
                        <th>Cost</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="res in reservations" :key="res.reservation_id">
                        <td>
                          <span :class="{'badge bg-success': res.status === 'Active', 'badge bg-warning text-dark': res.status === 'Needs Payment', 'badge bg-secondary': res.status === 'Paid'}">{{ res.status }}</span>
                        </td>
                        <td>{{ res.lot_location || '-' }}</td>
                        <td>{{ res.vehicle_number || '-' }}</td>
                        <td>{{ toIST(res.parking_timestamp) }}</td>
                        <td>{{ res.release_timestamp ? toIST(res.release_timestamp) : '-' }}</td>
                        <td>₹{{ res.parking_cost ? res.parking_cost.toFixed(2) : 'N/A' }}</td>
                        <td>
                          <button v-if="res.status === 'Active'" class="btn btn-warning btn-sm" @click="openVacateModal(res)">Vacate Spot</button>
                          <button v-if="res.status === 'Needs Payment'" class="btn btn-success btn-sm" @click="payNow(res.reservation_id)">Pay Now</button>
                          <span v-if="res.status === 'Paid'" class="text-muted fst-italic">Payment Complete</span>
                        </td>
                      </tr>
                    </tbody>
                </table>

                <h3 class="mt-5">Available Parking Lots</h3>
                <div v-if="lots.length === 0" class="alert alert-warning">
                    No parking lots available at the moment. Please check back later.
                </div>
                <table v-else class="table">
                    <thead><tr><th>Location</th><th>Price (per hr)</th><th>Available Spots</th><th>Action</th></tr></thead>
                    <tbody>
                        <tr v-for="lot in lots" :key="lot.id">
                            <td>{{ lot.location }}</td>
                            <td>₹{{ lot.price.toFixed(2) }}</td>
                            <td>{{ lot.available_spots }}</td>
                            <td>
                                <button class="btn btn-success" :disabled="lot.available_spots === 0 || hasActiveBooking" @click="openBookingModal(lot.id)">
                                    Book Now
                                </button>
                                <button class="btn btn-info ms-2" @click="showLotDetails(lot)">Details</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- #################### USER STATS VIEW #################### -->
            <div v-if="showView === 'user_stats'">
                <button class="btn btn-secondary mb-3" @click="showView = 'book_parking'">Back</button>
                <h3>My Parking Summary</h3>
                <div class="row">
                    <div class="col-md-6">
                        <h4>Reservations per Month</h4>
                        <canvas id="userReservationsChart"></canvas>
                    </div>
                    <div class="col-md-6">
                        <h4>Amount Spent per Month</h4>
                        <canvas id="userSpentChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- #################### BOOKING MODAL (New) #################### -->
        <div class="modal fade" id="bookingModal" tabindex="-1" aria-labelledby="bookingModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="bookingModalLabel">Book a Parking Spot</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>You are booking a spot in Lot ID: {{ bookingLotId }}</p>
                        <div class="mb-3">
                            <label for="vehicleNumber" class="form-label">Vehicle Number</label>
                            <input type="text" class="form-control" id="vehicleNumber" v-model="vehicleNumber" placeholder="e.g., UP32 L 1234">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" @click="confirmBooking">Confirm Booking</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- #################### VACATE SPOT MODAL #################### -->
        <div class="modal fade" id="vacateModal" tabindex="-1" aria-labelledby="vacateModalLabel" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header bg-warning">
                <h5 class="modal-title" id="vacateModalLabel">Release the parking spot</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body" v-if="vacateReservation">
                <div class="mb-2"><strong>Spot ID:</strong> {{ vacateReservation.spot_id }}</div>
                <div class="mb-2"><strong>Vehicle Number:</strong> {{ vacateReservation.vehicle_number }}</div>
                <div class="mb-2"><strong>Parking Time (IST):</strong> {{ toIST(vacateReservation.parking_timestamp) }}</div>
                <div class="mb-2"><strong>Releasing Time (IST):</strong> {{ toIST(vacateTime) }}</div>
                <div class="mb-2"><strong>Total Cost:</strong> {{ vacateCost !== null ? '₹' + vacateCost.toFixed(2) : '-' }}</div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" v-if="!vacateReleased">Cancel</button>
                <button type="button" class="btn btn-primary" @click="confirmVacate" v-if="!vacateReleased">Release</button>
                <button type="button" class="btn btn-success" data-bs-dismiss="modal" v-if="vacateReleased">Close</button>
              </div>
            </div>
          </div>
        </div>

        <!-- #################### VIEW SPOTS MODAL #################### -->
        <div class="modal fade" id="spotsModal" tabindex="-1" aria-labelledby="spotsModalLabel" aria-hidden="true">
          <div class="modal-dialog modal-lg">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="spotsModalLabel">
                  Parking Spots for {{ spotsLotName }}
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                <table class="table table-bordered">
                  <thead>
                    <tr>
                      <th>Spot ID</th>
                      <th>Status</th>
                      <th>Vehicle Number</th>
                      <th>User Email</th>
                      <th>Parked Since</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="spot in lotSpots" :key="spot.id">
                      <td>{{ spot.id }}</td>
                      <td>
                        <span :class="{'badge bg-success': spot.status === 'Available', 'badge bg-danger': spot.status === 'Occupied'}">
                          {{ spot.status }}
                        </span>
                      </td>
                      <td>{{ spot.vehicle_number || '-' }}</td>
                      <td>{{ spot.user_email || '-' }}</td>
                      <td>{{ spot.parked_since ? toIST(spot.parked_since) : '-' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
    </div>
    `,
    data() {
        return {
            loading: true,
            userEmail: sessionStorage.getItem("user_email") || '',
            userRole: '',
            authToken: sessionStorage.getItem("auth_token"),
            showView: 'book_parking',
            lots: [],
            reservations: [],
            newLot: { location: '', price: 0, address: '', pin: '', spots: 0 },
            userUname: sessionStorage.getItem("user_uname") || '',
            selectedLot: null,
            // --- Modal-related properties ---
            bookingModal: null,
            bookingLotId: null,
            vehicleNumber: '',
            vacateModal: null,
            vacateReservation: null,
            vacateCost: null,
            vacateTime: null,
            vacateReleased: false,
            adminStats: {},
            occupancyChart: null,
            revenueChart: null,
            userStats: [],
            userReservationsChart: null,
            userSpentChart: null,
            allUsers: [], // <-- Add this line
            lotSpots: [],
            spotsLotName: '',
            spotsModal: null,
        };
    },
    computed: {
        hasActiveBooking() {
            return this.reservations.some(r => r.status === 'Active');
        }
    },
    methods: {
        async apiFetch(url, options = {}) {
            const headers = {
                'Content-Type': 'application/json',
                'Authentication-Token': this.authToken, ...options.headers };
            const response = await fetch(url, { ...options, headers });
            if (!response.ok) {
                const errorData = await response.json();
                alert(`Error: ${errorData.message}`);
                throw new Error(errorData.message || 'API request failed');
            }
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return response.json();
            }
            return {}; // Return empty object for non-json responses (like DELETE)
        },

        // --------- ADMIN METHODS (with full CRUD) ---------
        async fetchLots() {
            try {
                this.lots = (await this.apiFetch('/api/admin/parking-lots')).parking_lots;
                this.showView = 'view_lots';
            } catch (error) { console.error("Failed to fetch lots:", error); }
        },
        showAddForm() {
            this.newLot = { location: '', price: 0, address: '', pin: '', spots: 0 };
            this.showView = 'add_lot';
        },
        showEditForm(lot) {
            // Create a copy of the lot object to avoid modifying the original list directly
            this.editLotData = { ...lot };
            this.showView = 'edit_lot';
        },
        cancelForm() {
            this.showView = 'view_lots';
            this.editLotData = null; // Clear edit data
        },
        async createLot() {
            if (!this.newLot.location || this.newLot.price <= 0 || this.newLot.spots <= 0) { alert('Please fill all fields correctly.'); return; }
            try {
                const data = await this.apiFetch('/api/admin/parking-lots', { method: 'POST', body: JSON.stringify(this.newLot) });
                alert(data.message); this.fetchLots(); // Refresh list after creating
            } catch (error) { console.error("Failed to create lot:", error); }
        },
        async updateLot() {
            if (!this.editLotData) return;
            try {
                const payload = {
                    location: this.editLotData.location,
                    price: this.editLotData.price,
                    address: this.editLotData.address,
                    pin: this.editLotData.pin,
                    spots: Number(this.editLotData.spots), 
                };
                const data = await this.apiFetch(`/api/admin/parking-lots/${this.editLotData.id}`, { method: 'PUT', body: JSON.stringify(payload) });
                alert(data.message);
                this.fetchLots(); // Refresh list after updating
            } catch (error) { console.error("Failed to update lot:", error); }
        },
        async deleteLot(lotId) {
            if (!confirm('Are you sure you want to delete this parking lot? This cannot be undone.')) { return; }
            try {
                const data = await this.apiFetch(`/api/admin/parking-lots/${lotId}`, { method: 'DELETE' });
                alert(data.message); this.fetchLots(); // Refresh list after deleting
            } catch (error) { console.error("Failed to delete lot:", error); }
        },
        // --------- USER METHODS (Updated for Modal Flow) ---------
        openBookingModal(lotId) {
            this.bookingLotId = lotId;
            this.vehicleNumber = '';
            if (!this.bookingModal) {
                this.bookingModal = new bootstrap.Modal(document.getElementById('bookingModal'));
            }
            this.bookingModal.show();
        },
        async confirmBooking() {
            if (!this.vehicleNumber) {
                alert('Please enter a vehicle number.');
                return;
            }
            try {
                const payload = {
                    lot_id: this.bookingLotId,
                    vehicle_number: this.vehicleNumber
                };
                const data = await this.apiFetch('/api/user/reserve-parking', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                alert(data.message);
                this.bookingModal.hide();
                this.fetchInitialUserData();
            } catch (error) {
                console.error("Failed to confirm booking:", error);
            }
        },
        async openVacateModal(reservation) {
            this.vacateReservation = reservation;
            this.vacateCost = null;
            this.vacateTime = null;
            this.vacateReleased = false;
            if (!this.vacateModal) {
                this.vacateModal = new bootstrap.Modal(document.getElementById('vacateModal'));
            }
            this.vacateModal.show();
        },
        async confirmVacate() {
            try {
                const data = await this.apiFetch('/api/user/vacate-parking', { method: 'POST' });
                this.vacateCost = data.final_cost;
                this.vacateTime = data.vacated_at;
                // Instead of hiding the modal immediately, show the info and let user close
                // Optionally, set a flag to show a "Close" button
                this.vacateReleased = true;
                // Optionally, refresh data
                this.fetchInitialUserData();
            } catch (error) {
                console.error("Failed to vacate spot:", error);
            }
        },
        openViewSpotsModal(lotName, spots) {
            this.spotsLotName = lotName;
            this.lotSpots = spots;
            if (!this.spotsModal) {
                this.spotsModal = new bootstrap.Modal(document.getElementById('spotsModal'));
            }
            this.spotsModal.show();
        },
        async fetchInitialUserData() {
            // This function will get all necessary data for the user dashboard at once.
            await this.fetchUserReservations();
            await this.fetchAvailableLots();
        },
        async fetchAvailableLots() {
            try {
                const endpoint = this.userRole === 'admin'
                    ? '/api/admin/parking-lots'
                    : '/api/user/parking-lots';
                const data = await this.apiFetch(endpoint);
                this.lots = data.parking_lots;
            } catch (error) {
                console.error("Failed to fetch available lots:", error);
            }
        },
        async fetchUserReservations() {
            try {
                const data = await this.apiFetch('/api/user/reservations');
                this.reservations = data.reservations.map(res => {
                    if (res.status === 'Completed') {
                        res.status = res.paid ? 'Paid' : 'Needs Payment';
                    }
                    return res;
                }).sort((a, b) => (a.status === 'Active' ? -1 : 1));
            } catch (error) { console.error("Failed to fetch user reservations:", error); }
        },
        async vacateSpot() {
            try {
                const data = await this.apiFetch('/api/user/vacate-parking', { method: 'POST' });
                alert(data.message); this.fetchInitialUserData();
            } catch (error) { console.error("Failed to vacate spot:", error); }
        },
        async payNow(reservationId) {
            try {
                const data = await this.apiFetch(`/api/user/payment/${reservationId}`, { method: 'POST' });
                alert(data.message);
                // Mark as paid locally to update UI instantly before refetching
                const reservation = this.reservations.find(r => r.reservation_id === reservationId);
                if (reservation) {
                    reservation.paid = true;
                    reservation.status = 'Paid'; // <-- Add this line!
                }
                // Optionally, you can also refetch all data:
                // await this.fetchInitialUserData();
            } catch (error) {
                console.error("Payment failed:", error);
            }
        },
        toIST(isoString) {
            if (!isoString) return '-';
            const date = new Date(isoString);
            return date.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' });
        },
        showLotDetails(lot) {
            this.selectedLot = lot;
        },
        async fetchAdminStats() {
            // Fetch occupancy data
            const summary = await this.apiFetch('/api/admin/summary');
            this.adminStats = { occupancy: summary };

            // Fetch revenue data (implement this endpoint in Flask)
            const revenue = await this.apiFetch('/api/admin/revenue-summary');
            this.adminStats.revenue = revenue;

            this.$nextTick(() => {
                this.renderAdminCharts();
            });
        },
        renderAdminCharts() {
            // Occupancy Doughnut
            if (this.occupancyChart) this.occupancyChart.destroy();
            const occ = this.adminStats.occupancy.overall_occupancy;
            const occCtx = document.getElementById('occupancyChart').getContext('2d');
            this.occupancyChart = new Chart(occCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Occupied', 'Available'],
                    datasets: [{
                        data: [occ.occupied, occ.available],
                        backgroundColor: ['#ff6384', '#36a2eb']
                    }]
                }
            });

            // Revenue Bar
            if (this.revenueChart) this.revenueChart.destroy();
            const rev = this.adminStats.revenue.lots;
            const revCtx = document.getElementById('revenueChart').getContext('2d');
            this.revenueChart = new Chart(revCtx, {
                type: 'bar',
                data: {
                    labels: rev.map(l => l.name),
                    datasets: [{
                        label: 'Revenue (₹)',
                        data: rev.map(l => l.revenue),
                        backgroundColor: '#4bc0c0'
                    }]
                }
            });
        },
        async fetchUserStats() {
            try {
                const data = await this.apiFetch('/api/user/reports');
                this.userStats = data.reports;
                console.log("User stats:", this.userStats); // <-- Add this line
                this.$nextTick(() => {
                    this.renderUserCharts();
                });
            } catch (error) {
                console.error("Failed to fetch user stats:", error);
            }
        },
        renderUserCharts() {
            if (this.userReservationsChart) this.userReservationsChart.destroy();
            if (this.userSpentChart) this.userSpentChart.destroy();

            // Convert "YYYY-MM" to "Month YYYY"
            const months = this.userStats.map(r => {
                const [year, month] = r.month.split('-');
                const date = new Date(year, month - 1); // JS months are 0-based
                return date.toLocaleString('default', { month: 'long', year: 'numeric' });
            });
            const reservations = this.userStats.map(r => r.total_reservations);
            const spent = this.userStats.map(r => r.total_spent);

            // Reservations per Month
            const resCtx = document.getElementById('userReservationsChart').getContext('2d');
            this.userReservationsChart = new Chart(resCtx, {
                type: 'bar',
                data: {
                    labels: months,
                    datasets: [{
                        label: 'Reservations',
                        data: reservations,
                        backgroundColor: '#36a2eb'
                    }]
                }
            });

            // Amount Spent per Month
            const spentCtx = document.getElementById('userSpentChart').getContext('2d');
            this.userSpentChart = new Chart(spentCtx, {
                type: 'bar',
                data: {
                    labels: months,
                    datasets: [{
                        label: 'Amount Spent (₹)',
                        data: spent,
                        backgroundColor: '#ff6384'
                    }]
                }
            });
        },
        async fetchAllUsers() {
            try {
                const data = await this.apiFetch('/api/admin/users');
                this.allUsers = data.users;
            } catch (error) {
                console.error("Failed to fetch users:", error);
            }
        },
        async viewSpots(lot) {
            try {
                const data = await this.apiFetch(`/api/admin/parking-lots/${lot.id}/spots`);
                this.lotSpots = data.spots;
                this.spotsLotName = lot.location;
                if (!this.spotsModal) {
                    this.spotsModal = new bootstrap.Modal(document.getElementById('spotsModal'));
                }
                this.spotsModal.show();
            } catch (error) {
                alert("Failed to fetch spot details.");
            }
        },
    },
    async mounted() {
        if (!this.authToken) { this.$router.push('/login'); return; }
        const roles = JSON.parse(sessionStorage.getItem("user_roles") || '[]');
        this.userRole = roles.includes('admin') ? 'admin' : 'user';

        if (this.userRole === 'admin') {
            await this.fetchLots();
            await this.fetchAllUsers(); // <-- Add this line
            this.showView = 'view_lots';
        } else {
            await this.fetchInitialUserData();
            this.showView = 'book_parking';
        }
        this.loading = false;
    }
}
