export default {
    name: 'FooterComponent',
    template: `
        <footer class="bg-light text-center text-lg-start fixed-bottom">
            <div class="text-center p-2 border-top">
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
