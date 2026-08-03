document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const loginForm = document.getElementById("login-form");
  const userInfo = document.getElementById("user-info");
  const currentUserEmail = document.getElementById("current-user-email");
  const currentUserBranch = document.getElementById("current-user-branch");
  const logoutButton = document.getElementById("logout-button");

  let currentUser = null;

  function showMessage(text, type = "info") {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  function setAuthenticated(user) {
    currentUser = user;
    if (user) {
      loginForm.classList.add("hidden");
      userInfo.classList.remove("hidden");
      currentUserEmail.textContent = user.email;
      currentUserBranch.textContent = user.branch;
    } else {
      loginForm.classList.remove("hidden");
      userInfo.classList.add("hidden");
      currentUserEmail.textContent = "";
      currentUserBranch.textContent = "";
    }
  }

  async function fetchCurrentUser() {
    try {
      const response = await fetch("/me");
      if (!response.ok) {
        setAuthenticated(null);
        return;
      }
      const user = await response.json();
      setAuthenticated(user);
    } catch (error) {
      console.error("Error checking login status:", error);
      setAuthenticated(null);
    }
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map((email) => {
                    const canUnregister = currentUser && currentUser.email === email;
                    return `<li><span class="participant-email">${email}</span>${
                      canUnregister
                        ? `<button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button>`
                        : ""
                    }</li>`;
                  })
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to unregister. Please try again.", "error");
      console.error("Error unregistering:", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!currentUser) {
      showMessage("Please log in before signing up.", "error");
      return;
    }

    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    try {
      const response = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const result = await response.json();
      if (response.ok) {
        setAuthenticated(result);
        showMessage("Logged in successfully.", "success");
        fetchActivities();
        loginForm.reset();
      } else {
        showMessage(result.detail || "Invalid login.", "error");
      }
    } catch (error) {
      showMessage("Login failed. Please try again.", "error");
      console.error("Error logging in:", error);
    }
  });

  logoutButton.addEventListener("click", async () => {
    try {
      const response = await fetch("/logout", {
        method: "POST",
      });
      if (response.ok) {
        setAuthenticated(null);
        showMessage("Logged out successfully.", "success");
        fetchActivities();
      } else {
        showMessage("Logout failed.", "error");
      }
    } catch (error) {
      showMessage("Logout failed. Please try again.", "error");
      console.error("Error logging out:", error);
    }
  });

  fetchCurrentUser().then(fetchActivities);
});
