// Мобильная навигация
document.addEventListener("DOMContentLoaded", function () {
  const navToggle = document.getElementById("nav-toggle");
  const navMenu = document.getElementById("nav-menu");

  if (navToggle && navMenu) {
    navToggle.addEventListener("click", function () {
      navMenu.classList.toggle("active");
      navToggle.classList.toggle("active");
    });

    // Закрытие меню при клике на ссылку
    const navLinks = document.querySelectorAll(".nav-link");
    navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        navMenu.classList.remove("active");
        navToggle.classList.remove("active");
      });
    });

    // Закрытие меню при клике вне его
    document.addEventListener("click", function (event) {
      if (!navToggle.contains(event.target) && !navMenu.contains(event.target)) {
        navMenu.classList.remove("active");
        navToggle.classList.remove("active");
      }
    });
  }
});

// Автоматическое скрытие флеш-сообщений
document.addEventListener("DOMContentLoaded", function () {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.transition = "opacity 0.5s ease";
      alert.style.opacity = "0";
      setTimeout(() => {
        alert.remove();
      }, 500);
    }, 5000);
  });
});

// Подтверждение удаления
function confirmDelete(message = "Вы уверены, что хотите удалить этот элемент?") {
  return confirm(message);
}

// Функции для работы с пользователями
function editUser(userId) {
  // Здесь можно добавить модальное окно для редактирования
  alert("Функция редактирования пользователя будет добавлена позже");
}

function deleteUser(userId) {
  if (confirmDelete("Вы уверены, что хотите удалить этого пользователя?")) {
    // Здесь будет AJAX запрос на удаление
    alert("Функция удаления пользователя будет добавлена позже");
  }
}

// Анимация загрузки для форм
function showLoading(button) {
  const originalText = button.innerHTML;
  button.innerHTML = '<span class="loading"></span> Загрузка...';
  button.disabled = true;

  return function () {
    button.innerHTML = originalText;
    button.disabled = false;
  };
}

// Валидация форм
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return true;

  const requiredFields = form.querySelectorAll("[required]");
  let isValid = true;

  requiredFields.forEach((field) => {
    if (!field.value.trim()) {
      field.style.borderColor = "#dc3545";
      isValid = false;
    } else {
      field.style.borderColor = "#e1e1e1";
    }
  });

  return isValid;
}

// Форматирование числовых полей
document.addEventListener("DOMContentLoaded", function () {
  const numberInputs = document.querySelectorAll('input[type="number"]');
  numberInputs.forEach((input) => {
    input.addEventListener("input", function () {
      if (this.value < 0) {
        this.value = 0;
      }
    });
  });
});

// Предварительный просмотр изображений
function previewImage(input, previewId) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const preview = document.getElementById(previewId);
      if (preview) {
        preview.src = e.target.result;
        preview.style.display = "block";
      }
    };
    reader.readAsDataURL(input.files[0]);
  }
}

// Утилиты для работы с таблицами
function sortTable(tableId, columnIndex, dataType = "string") {
  const table = document.getElementById(tableId);
  if (!table) return;

  const tbody = table.querySelector("tbody");
  const rows = Array.from(tbody.querySelectorAll("tr"));

  rows.sort((a, b) => {
    const aVal = a.cells[columnIndex].textContent.trim();
    const bVal = b.cells[columnIndex].textContent.trim();

    if (dataType === "number") {
      return parseFloat(aVal) - parseFloat(bVal);
    } else if (dataType === "date") {
      return new Date(aVal) - new Date(bVal);
    } else {
      return aVal.localeCompare(bVal);
    }
  });

  rows.forEach((row) => tbody.appendChild(row));
}

// Фильтрация таблиц
function filterTable(tableId, searchInputId) {
  const searchInput = document.getElementById(searchInputId);
  const table = document.getElementById(tableId);

  if (!searchInput || !table) return;

  searchInput.addEventListener("input", function () {
    const filter = this.value.toLowerCase();
    const rows = table.querySelectorAll("tbody tr");

    rows.forEach((row) => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(filter) ? "" : "none";
    });
  });
}

// Экспорт данных
async function exportData(url, filename) {
  try {
    const response = await fetch(url);
    const blob = await response.blob();

    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  } catch (error) {
    console.error("Ошибка при экспорте:", error);
    alert("Произошла ошибка при экспорте данных");
  }
}

// Печать страницы
function printPage() {
  window.print();
}

// Копирование в буфер обмена
function copyToClipboard(text) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      // Показать уведомление об успешном копировании
      showNotification("Скопировано в буфер обмена", "success");
    })
    .catch((err) => {
      console.error("Ошибка копирования:", err);
    });
}

// Показ уведомлений
function showNotification(message, type = "info", duration = 3000) {
  const notification = document.createElement("div");
  notification.className = `alert alert-${type}`;
  notification.style.position = "fixed";
  notification.style.top = "20px";
  notification.style.right = "20px";
  notification.style.zIndex = "9999";
  notification.style.minWidth = "300px";
  notification.innerHTML = `
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.remove();
  }, duration);
}
