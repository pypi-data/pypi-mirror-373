function getByPatternId(partial) {
    // match on three independent fragments so key order doesn’t matter
    const s = `[id*='"component":"${partial.component}"']` +
        `[id*='"subcomponent":"${partial.subcomponent}"']` +
        `[id*='"aio_id":"${partial.aio_id}"']`;
    return document.querySelector(s);
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    mainLayout: {
        inputUpdate: function (_, textareaId, buttonId, counter) {
            // textareaId/buttonId are the actual DOM ids (Dash stringifies dict ids)
            const ta = getByPatternId(textareaId);
            const btn = getByPatternId(buttonId);

            if (!ta || !btn) return window.dash_clientside.no_update;

            ta.parentNode.dataset.replicatedValue = ta.value;

            // Only bind once
            if (ta.dataset.cmdBound === "1") {
                return window.dash_clientside.no_update;
            }
            ta.dataset.cmdBound = "1";

            ta.addEventListener("keydown", function (e) {
                // const isMac = navigator.userAgentData
                //     ? navigator.userAgentData.platform.toUpperCase().includes(
                //         "MAC",
                //     )
                //     : navigator.userAgent.toUpperCase().includes("MAC");

                // const combo = (isMac ? e.metaKey : e.ctrlKey) &&
                //     e.key === "Enter";

                // if (e.key === "Enter") {
                //     e.preventDefault();
                //     btn.click();
                // }

                if (e.key === "Enter" && e.shiftKey) {
                    // Allow line breaks
                    return;
                }
                if (e.key === "Enter") {
                    e.preventDefault();
                    btn.click();
                }
            });

            // bump a counter just to produce a deterministic return
            return (counter || 0) + 1;
        },
    },
});
