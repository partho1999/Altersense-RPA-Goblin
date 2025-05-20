module.exports = {
  content: [
    "./templates/**/*.html", //new
  ],
  theme: {
    extend: {
      backgroundColor: {
        // primary: "white",
      },
    },
  },
  plugins: [require("daisyui")],
};
