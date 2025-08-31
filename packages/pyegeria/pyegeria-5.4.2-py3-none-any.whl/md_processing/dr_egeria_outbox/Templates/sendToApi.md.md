<%* 
// Access note frontmatter
const id = tp.frontmatter.id;
const title = tp.frontmatter.title;

// Make a RESTful POST request
const response = await fetch("https://httpbin.org/post", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id, title })
});

const result = await response.json();

// Show result in Obsidian notification
new Notice("API call complete: " + JSON.stringify(result.json));
%>
