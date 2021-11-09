var customBarColors = {
  success:'#28a745',
  error: '#dc3545',
  ignored:'#7a7a7a',
  progress:'#007bff',
}

function customProgress(progressBarElement, progressBarMessageElement, progress) {
  if (progress.current == 0) {
      if (progress.pending === true) {
          progressBarMessageElement.textContent = 'Waiting for task to start...';
      } else {
          progressBarMessageElement.textContent = 'Task started...';
      }
  } else {
      progressBarMessageElement.textContent = progress.description;
  }
    console.log(progressBarElement);
    console.log(progressBarMessageElement);
    console.log(progress);
    progressBarElement.style.width = String(progress.percent) + "%";
    progressBarElement.style.background = this.barColors.progress;
  }

  function customSuccess(progressBarElement, progressBarMessageElement) {
    progressBarElement.style.background = this.barColors.success;
    progressBarMessageElement.innerHTML = 'Completed!';
  }

  function customError(progressBarElement, progressBarMessageElement) {
    progressBarElement.style.background = this.barColors.error;
    progressBarMessageElement.innerHTML = 'Something Went Wrong!';
  }

  function check_link() {
    var link_element = document.getElementsByName('link')[0];
    var link = link_element.value;
    var modal_text = document.getElementById('modal_text');
    console.log(link);

    if (link.length === 0) {
      modal_text.innerHTML = "Enter A Link!";
      link_element.click();
      return false;
    } else {
      // Validate The Link
      if (link.endsWith(".onion")) {
        modal_text.innerHTML = "Wait for a while, while we process the link ...";
        // Show Progress Bar Here
        document.getElementsByName('link_form')[0].submit();
        link_element.click();
        return true;
      } else {
        modal_text.innerHTML = "Enter An Onion Link!";
        link_element.click();
        return false;
      }
    }
}
