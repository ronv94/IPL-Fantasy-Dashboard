window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

window.dashAgGridComponentFunctions.rankChangeRenderer = function (params) {
    const rank = params.value;
    const iconInfo = params.data["Rank Change Icon"];

    return React.createElement(
        "span",
        { className: "rank-change-icon" },
        React.createElement(
            "span",
            {
                className: "icon-placeholder",
                dangerouslySetInnerHTML: { __html: iconInfo || "" }
            }
        ),
        React.createElement(
            "span",
            { className: "rank-text" },
            rank
        )
    );
};
