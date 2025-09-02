document.addEventListener("DOMContentLoaded", function () {
  const handleChange = (event) => {
    const { value } = event.target;
    const currentPath = window.location.pathname;
    const countryCodeRegex = /^\/[a-z]{2}\//;
    const currentPathWithoutCountryCode = currentPath.replace(
      countryCodeRegex,
      "/"
    );
    const newPath = "/" + value + currentPathWithoutCountryCode;
    event.target.selectedIndex = Array.from(event.target.options).findIndex(
      (option) => option.hasAttribute("selected")
    );
    window.location.pathname = newPath;
  };
  const languageSwitchers = document.querySelectorAll("#iati-country-switcher");
  languageSwitchers.forEach((languageSwitcher) => {
    languageSwitcher.addEventListener("change", handleChange);
  });
});
