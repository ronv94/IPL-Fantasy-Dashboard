window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

window.dashAgGridComponentFunctions.rankChangeRenderer = function (params) {
    const rank = params.value;
    const iconInfo = params.data["Rank Change Icon"];
    let svgIcon = "";

    if (iconInfo && iconInfo.icon === "triangle-up") {
        svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="14" height="10" viewBox="0 0 14 10" fill="none">
<path d="M1 10C0.814289 10 0.632245 9.94829 0.474269 9.85065C0.316293 9.75302 0.188626 9.61332 0.105573 9.44721C0.0225203 9.28111 -0.0126368 9.09516 0.00404117 8.91019C0.0207191 8.72523 0.0885731 8.54857 0.2 8.4L6.2 0.4C6.29315 0.275804 6.41393 0.175 6.55279 0.105573C6.69164 0.036145 6.84476 0 7 0C7.15525 0 7.30836 0.036145 7.44721 0.105573C7.58607 0.175 7.70685 0.275804 7.8 0.4L13.8 8.4C13.9114 8.54857 13.9793 8.72523 13.996 8.91019C14.0126 9.09516 13.9775 9.28111 13.8944 9.44721C13.8114 9.61332 13.6837 9.75302 13.5257 9.85065C13.3678 9.94829 13.1857 10 13 10H1Z" fill="#51CF66"/>
</svg>`;
    } else if (iconInfo && iconInfo.icon === "triangle-down") {
        svgIcon = `<svg width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M1 0C0.814289 0 0.632245 0.0517147 0.474269 0.149349C0.316293 0.246984 0.188626 0.386681 0.105573 0.552787C0.0225203 0.718893 -0.0126368 0.904844 0.00404117 1.08981C0.0207191 1.27477 0.0885731 1.45143 0.2 1.6L6.2 9.6C6.29315 9.7242 6.41393 9.825 6.55279 9.89443C6.69164 9.96385 6.84476 10 7 10C7.15525 10 7.30836 9.96385 7.44721 9.89443C7.58607 9.825 7.70685 9.7242 7.8 9.6L13.8 1.6C13.9114 1.45143 13.9793 1.27477 13.996 1.08981C14.0126 0.904844 13.9775 0.718893 13.8944 0.552787C13.8114 0.386681 13.6837 0.246984 13.5257 0.149349C13.3678 0.0517147 13.1857 0 13 0H1Z" fill="#FF6B6B"/>
</svg>`;
    }

    const wrapper = document.createElement("span");
    wrapper.innerHTML = `${rank}${svgIcon}`;
    return wrapper;
};
