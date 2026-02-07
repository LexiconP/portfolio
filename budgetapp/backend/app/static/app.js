// Simple UI logic for uploading receipts and managing budgets.
const uploadForm = document.getElementById("upload-form");
const receiptFile = document.getElementById("receipt-file");
const uploadStatus = document.getElementById("upload-status");
const receiptsList = document.getElementById("receipts-list");
const refreshReceipts = document.getElementById("refresh-receipts");
const budgetForm = document.getElementById("budget-form");
const budgetsList = document.getElementById("budgets-list");

async function fetchReceipts() {
  // Load receipts from the API and render them.
  const response = await fetch("/receipts");
  const receipts = await response.json();
  receiptsList.innerHTML = "";

  if (!receipts.length) {
    receiptsList.innerHTML = "<li>No receipts yet.</li>";
    return;
  }

  receipts.forEach((receipt) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span>${receipt.vendor || "Unknown"} — ${receipt.total || 0}</span>
      <span>${receipt.date || ""}</span>
    `;
    receiptsList.appendChild(li);
  });
}

async function fetchBudgets() {
  // Load budgets from the API and render them.
  const response = await fetch("/budgets");
  const budgets = await response.json();
  budgetsList.innerHTML = "";

  if (!budgets.length) {
    budgetsList.innerHTML = "<li>No budgets yet.</li>";
    return;
  }

  budgets.forEach((budget) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span>${budget.category}</span>
      <span>${budget.spent} / ${budget.monthly_limit}</span>
    `;
    budgetsList.appendChild(li);
  });
}

uploadForm.addEventListener("submit", async (event) => {
  // Upload a receipt image.
  event.preventDefault();
  if (!receiptFile.files.length) {
    return;
  }

  const formData = new FormData();
  formData.append("file", receiptFile.files[0]);
  uploadStatus.textContent = "Uploading...";

  try {
    const response = await fetch("/receipts", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const message = await response.json();
      uploadStatus.textContent = message.detail || "Upload failed";
      return;
    }

    uploadStatus.textContent = "Receipt uploaded.";
    receiptFile.value = "";
    fetchReceipts();
  } catch (error) {
    uploadStatus.textContent = "Upload failed.";
  }
});

refreshReceipts.addEventListener("click", () => {
  // Manual refresh for receipts list.
  fetchReceipts();
});

budgetForm.addEventListener("submit", async (event) => {
  // Submit a budget update.
  event.preventDefault();

  const category = document.getElementById("budget-category").value.trim();
  const monthlyLimit = parseFloat(
    document.getElementById("budget-limit").value
  );
  const spent = parseFloat(document.getElementById("budget-spent").value);

  if (!category) {
    return;
  }

  await fetch("/budgets", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      category,
      monthly_limit: monthlyLimit,
      spent,
    }),
  });

  budgetForm.reset();
  fetchBudgets();
});

fetchReceipts();
fetchBudgets();
