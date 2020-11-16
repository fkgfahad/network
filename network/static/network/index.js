const postsContainer = document.getElementById('posts');

function showMessage(msg, err = true) {
  const messageContainer = document.getElementById('message');
  if (!msg) {
    messageContainer.innerText = '';
    messageContainer.className = '';
    messageContainer.style.display = 'none';
  } else {
    messageContainer.className = `text-center alert alert-${err ? 'danger' : 'success'}`;
    messageContainer.innerText = msg;
    messageContainer.style.display = 'block';
  }
}

const newPost = document.getElementById('newPost');
if (newPost) {
  newPost.onsubmit = (_) => {
    _.preventDefault();
    const content = _.target[0].value;
    if (!content) return;
    http
      .post('/new_post', { content })
      .then((data) => {
        if (data.error) {
          showMessage(data.error);
          return;
        }
        placePost(data.post);
        _.target[0].value = '';
      })
      .catch(http.catchError);
  };
}

function placePost({ id, content, date, likes, username }) {
  const div = document.createElement('div');
  div.className = 'card';
  div.innerHTML = `
    <div class="card-header">
      <div>
        <a href="/profile/${username}">@${username}</a>
        <div class="small">${date}</div>
      </div>
      <div>
        <button id="edit${id}" onclick="onEdit(this, ${id})" class="btn btn-warning btn-sm">Edit</button>
      </div>
    </div>
    <div class="card-body">
      <div id="content${id}" style="white-space: pre-wrap">${content}</div>
      <form id="form${id}" style="display: none">
        <textarea id="input${id}" rows="3" required>${content}</textarea>
        <button class="btn btn-sm btn-danger" type="button" onclick="cancelEdit(${id})">Cancel</button>
        <button class="btn btn-sm btn-success" type="button" onclick="saveEdit(${id})">Save</button>
      </form>
    </div>
    <div class="card-footer">
      <button onclick="toggleLike(this, ${id})" class="btn btn-sm btn-primary">
        <span>Like</span>
        <span class="badge badge-light">${likes}</span>
      </button>
    </div>
  `;
  postsContainer.prepend(div);
}
