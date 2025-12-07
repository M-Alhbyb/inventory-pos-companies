/**
 * Infinite Scroll Module
 * Reusable infinite scroll functionality for paginated lists
 */

class InfiniteScroll {
  constructor(options) {
    this.nextPage = options.nextPage;
    this.hasNext = options.hasNext;
    this.isLoading = false;

    // Elements
    this.container = document.querySelector(options.containerSelector);
    this.loadingSpinner = document.getElementById("loading-spinner");
    this.endOfList = document.getElementById("end-of-list");

    // Callbacks
    this.createRowHtml = options.createRowHtml;
    this.baseUrl = options.baseUrl || window.location.href;

    // Scroll container
    this.scrollContainer = document.querySelector("main.overflow-y-auto");

    // Bind scroll events
    this.bindEvents();
  }

  bindEvents() {
    const handleScroll = () => this.handleScroll();

    if (this.scrollContainer) {
      this.scrollContainer.addEventListener("scroll", handleScroll);
    }
    window.addEventListener("scroll", handleScroll);
  }

  handleScroll() {
    let scrolledToBottom = false;

    if (this.scrollContainer) {
      const { scrollTop, scrollHeight, clientHeight } = this.scrollContainer;
      scrolledToBottom = scrollTop + clientHeight >= scrollHeight - 200;
    } else {
      scrolledToBottom =
        window.innerHeight + window.scrollY >= document.body.offsetHeight - 200;
    }

    if (scrolledToBottom && this.hasNext && !this.isLoading) {
      this.loadMore();
    }
  }

  loadMore() {
    if (!this.hasNext || this.isLoading) return;

    this.isLoading = true;
    if (this.loadingSpinner) {
      this.loadingSpinner.classList.remove("hidden");
    }

    // Build URL with current filters
    const currentUrl = new URL(this.baseUrl);
    currentUrl.searchParams.set("page", this.nextPage);

    // Add delay for better UX
    setTimeout(() => {
      fetch(currentUrl.toString(), {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success && data.data) {
            // Append new rows
            data.data.forEach((item) => {
              const rowHtml = this.createRowHtml(item);
              this.container.insertAdjacentHTML("beforeend", rowHtml);
            });

            // Update state
            this.hasNext = data.has_next;
            this.nextPage = data.next_page_number;

            // Show end message
            if (!this.hasNext && this.endOfList) {
              this.endOfList.classList.remove("hidden");
            }
          }
        })
        .catch((error) => console.error("Infinite scroll error:", error))
        .finally(() => {
          this.isLoading = false;
          if (this.loadingSpinner) {
            this.loadingSpinner.classList.add("hidden");
          }
        });
    }, 500);
  }
}

// Export for use in templates
window.InfiniteScroll = InfiniteScroll;
