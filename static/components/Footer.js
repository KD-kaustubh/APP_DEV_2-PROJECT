// ./components/Footer.js

export default {
    name: 'FooterComponent',
    template: `
        <footer class="bg-light text-center text-lg-start mt-5">
            <div class="text-center p-3 border-top">
                © {{ currentYear }} Vehicle Parking App. All rights reserved.
            </div>
        </footer>
    `,
    data() {
        return {
            currentYear: new Date().getFullYear()
        };
    }
};
