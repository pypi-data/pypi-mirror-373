

module.exports = async (params) => {
    const { app, tp } = params;

    // Get the current file content
    const content = await app.vault.read(tp.file.find_tfile(tp.file.path(true)));

    // REST call
    fetch("https://your-api-endpoint.com/endpoint", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ note: content })
    })
    .then(res => res.json())
    .then(data => {
        new Notice("REST call success: " + JSON.stringify(data));
    })
    .catch(err => {
        new Notice("REST call failed: " + err);
    });
};