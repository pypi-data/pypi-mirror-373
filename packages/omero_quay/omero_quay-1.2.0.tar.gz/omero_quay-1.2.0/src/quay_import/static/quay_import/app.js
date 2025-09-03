//https://developer.mescius.com/spreadjs/docs/getstarted/quick-start/importing-files

function send_to_omero_quay() {
  var command_line_stub = "../../omero-quay/scripts/desktop_cli.py ";
  var server = "https://nte.omero-fbi.fr/post";
  var xlsx_content = document.getElementById("file-upload").files[0];
  var xhr = new XMLHttpRequest();
  xhr.open(
    "POST",
    String(command_line_stub) +
      String(xlsx_content.path) +
      String(" ") +
      String(server),
    true
  );
  xhr.send();
}

// Construct the API projects URL
// See https://omero.readthedocs.io/en/stable/developers/json-api.html#list-projects
var projectsUrl = PARAMS.API_BASE_URL + "m/projects/";

// Filter projects by Owner to only show 'your' projects
projectsUrl += "?owner=" + PARAMS.EXP_ID;

fetch(projectsUrl)
  .then((rsp) => rsp.json())
  .then((data) => {
    let projectCount = data.meta.totalCount;
    let projects = data.data;

    // Render html...
    let html = `
            <div>Total: ${projectCount} projects...</div>
            <ul>
                ${projects
                  .map((p) => `<li>${p.Name} (ID: ${p["@id"]})</li>`)
                  .join("")}
            </ul>`;

    document.getElementById("projects").innerHTML = html;
  });
