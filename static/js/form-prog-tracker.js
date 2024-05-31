document.getElementById('progress-form').addEventListener('submit', function(e) {
      e.preventDefault();

      // Get form values
      const date = document.getElementById('date').value;
      const skill = document.getElementById('skill').value;
      const attempts = document.getElementById('attempts').value;
      const successes = document.getElementById('successes').value;
      const notes = document.getElementById('notes').value;

      // Create new table row
      const newRow = document.createElement('tr');
      newRow.innerHTML = `
        <td>${date}</td>
        <td>${attempts}</td>
        <td>${successes}</td>
        <td>${notes}</td>
      `;

      // Find or create skill section
      let skillTableBody = document.getElementById(`table-body-${skill.toLowerCase()}`);
      if (!skillTableBody) {
        // Create new skill section
        const newSkillSection = document.createElement('div');
        newSkillSection.classList.add('card');
        newSkillSection.innerHTML = `
          <div class="card-header" id="heading${skill}">
            <h5 class="mb-0">
              <button class="btn btn-link collapsed" data-toggle="collapse" data-target="#collapse${skill}" aria-expanded="false" aria-controls="collapse${skill}">
                ${skill}
              </button>
            </h5>
          </div>
          <div id="collapse${skill}" class="collapse" aria-labelledby="heading${skill}" data-parent="#accordion">
            <div class="card-body">
              <table class="table table-striped">
                <thead class="thead-dark">
                  <tr>
                    <th scope="col">Date</th>
                    <th scope="col">Attempts</th>
                    <th scope="col">Successes</th>
                    <th scope="col">Notes</th>
                  </tr>
                </thead>
                <tbody id="table-body-${skill.toLowerCase()}">
                </tbody>
              </table>
            </div>
          </div>
        `;
        document.getElementById('accordion').appendChild(newSkillSection);
        skillTableBody = document.getElementById(`table-body-${skill.toLowerCase()}`);
      }

      // Append new row to the appropriate skill table body
      skillTableBody.appendChild(newRow);

      // Clear form
      document.getElementById('progress-form').reset();

      // Close modal
      $('#progressModal').modal('hide');
    });