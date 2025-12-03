// Modal elements

function AddModalFunction() {
  console.log("AddModalFunction");

  const AddModal = document.getElementById("addCategoryModal");
  AddModal.classList.remove("hidden");
  AddModal.classList.add("flex");
  document.body.style.overflow = "hidden";
  const closeModalBtn = document.getElementById("closeAddCategoryModal");
  const cancelBtn = document.getElementById("cancelAddCategory");
  const form = document.getElementById("addCategoryForm");
  const errorMessage = document.getElementById("errorMessage");

  // Open modal

  // Close modal function
  function closeModal() {
    AddModal.classList.add("hidden");
    AddModal.classList.remove("flex");
    document.body.style.overflow = "auto";
    form.reset();
    errorMessage.classList.add("hidden");
  }

  // Close modal events
  closeModalBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);

  // Close on backdrop click
  AddModal.addEventListener("click", (e) => {
    if (e.target === AddModal) {
      closeModal();
    }
  });

  // Close on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !AddModal.classList.contains("hidden")) {
      closeModal();
    }
  });

  // Form submission with AJAX
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      const data = await response.json();

      if (data.success) {
        // Close modal and reload page to show new product
        closeModal();
        location.reload();
      } else {
        // Show error message
        errorMessage.textContent = data.error || "حدث خطأ أثناء إضافة الفئة";
        errorMessage.classList.remove("hidden");
      }
    } catch (error) {
      errorMessage.textContent = "حدث خطأ في الاتصال بالخادم";
      errorMessage.classList.remove("hidden");
    }
  });
}

// Edit Modal elements
function EditModalFunction(productId) {
  const EditModal = document.getElementById("editCategoryModal");
  const openEditModalBtn = document.querySelectorAll(".openEditCategoryModal");
  EditModal.classList.remove("hidden");
  EditModal.classList.add("flex");
  document.body.style.overflow = "hidden";
  const closeModalBtn = document.getElementById("closeEditCategoryModal");
  const cancelBtn = document.getElementById("cancelEditCategory");
  const form = document.getElementById("editCategoryForm");
  const errorMessage = document.getElementById("errorMessage");

  // Get product data
  const categoryName = document.querySelector(
    ".category-name-" + productId
  ).textContent;
  const categoryDescription = document.querySelector(
    ".category-description-" + productId
  ).textContent;
  const formName = document.getElementById("editCategoryName");
  const formDescription = document.getElementById("editCategoryDescription");
  formName.value = categoryName;
  formDescription.value = categoryDescription;
  // Close modal function
  function closeModal() {
    EditModal.classList.add("hidden");
    EditModal.classList.remove("flex");
    document.body.style.overflow = "auto";
    form.reset();
    errorMessage.classList.add("hidden");
  }

  // Close modal events
  closeModalBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);

  // Close on backdrop click
  EditModal.addEventListener("click", (e) => {
    if (e.target === EditModal) {
      closeModal();
    }
  });

  // Close on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !EditModal.classList.contains("hidden")) {
      closeModal();
    }
  });

  // Form submission with AJAX
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    try {
      const response = await fetch(`/categories/edit/${productId}/`, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      const data = await response.json();

      if (data.success) {
        // Close modal and reload page to show new product
        closeModal();
        location.reload();
      } else {
        // Show error message
        errorMessage.textContent = data.error || "حدث خطأ أثناء تعديل الفئة";
        errorMessage.classList.remove("hidden");
      }
    } catch (error) {
      errorMessage.textContent = "حدث خطأ في الاتصال بالخادم";
      errorMessage.classList.remove("hidden");
    }
  });
}

// Delete Modal elements
function DeleteModalFunction(productId) {
  const DeleteModal = document.getElementById("deleteCategoryModal");
  const openDeleteModalBtn = document.querySelectorAll(
    ".openDeleteCategoryModal"
  );
  DeleteModal.classList.remove("hidden");
  DeleteModal.classList.add("flex");
  document.body.style.overflow = "hidden";
  const closeModalBtn = document.getElementById("closeDeleteCategoryModal");
  const cancelBtn = document.getElementById("cancelDeleteCategory");
  const form = document.getElementById("deleteCategoryForm");
  const errorMessage = document.getElementById("errorMessage");

  // Get product data
  const formName = document.getElementById("deleteCategoryName");
  const categoryName = document.querySelector(
    ".category-name-" + productId
  ).textContent;
  formName.textContent = categoryName;
  // Close modal function
  function closeModal() {
    DeleteModal.classList.add("hidden");
    DeleteModal.classList.remove("flex");
    document.body.style.overflow = "auto";
    form.reset();
    errorMessage.classList.add("hidden");
  }

  // Close modal events
  closeModalBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);

  // Close on backdrop click
  DeleteModal.addEventListener("click", (e) => {
    if (e.target === DeleteModal) {
      closeModal();
    }
  });

  // Close on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !DeleteModal.classList.contains("hidden")) {
      closeModal();
    }
  });

  // Form submission with AJAX
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    try {
      const response = await fetch(`/categories/delete/${productId}/`, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });

      const data = await response.json();

      if (data.success) {
        // Close modal and reload page to show new product
        closeModal();
        location.reload();
      } else {
        // Show error message
        errorMessage.textContent = data.error || "حدث خطأ أثناء حذف الفئة";
        errorMessage.classList.remove("hidden");
      }
    } catch (error) {
      errorMessage.textContent = "حدث خطأ في الاتصال بالخادم";
      errorMessage.classList.remove("hidden");
    }
  });
}
