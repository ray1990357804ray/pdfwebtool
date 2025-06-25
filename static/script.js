function simulateProgress(progressBar, callback) {
  let width = 0;
  progressBar.style.width = '0%';
  progressBar.parentElement.style.display = 'block'; // show progress container

  let interval = setInterval(() => {
    if (width >= 100) {
      clearInterval(interval);
      callback();
    } else {
      width += Math.floor(Math.random() * 10) + 5;
      if (width > 100) width = 100;
      progressBar.style.width = width + '%';
      progressBar.innerText = width + '%';
    }
  }, 300);
}

document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    const progressBar = this.querySelector('.progress-bar');
    if (!progressBar) {
      this.submit();
      return;
    }

    simulateProgress(progressBar, () => {
      this.submit();
    });
  });
});