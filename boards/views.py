# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count
import boards
from boards.models import Board, Post, Topic, User

from .forms import NewTopicForm, PostForm
from django.urls import reverse_lazy

def home(request):
    
    # boards_names = []

    # for board in boards:
    #     boards_names.append(board.name)

    # response_html = '<br>'.join(boards_names)
    # # print(response_html)
    return render(request, "home.html", context={"all_boards": Board.objects.all()})

@login_required
def board_topics(request, pk):
    # try:
    #     board_obj = Board.objects.get(pk=pk)
    # except Board.DoesNotExist:
    #     raise Http404
    board_obj = get_object_or_404(Board, pk=pk)
    topics = board_obj.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)

    return render(request, 'topics.html', {'board': board_obj, "all_topics": topics})

@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    # print(request.user)  # User object
    user = request.user #User.objects.first()  # TODO: get the currently logged in user
    if request.method == 'POST':
        form = NewTopicForm(request.POST)  # subject, message
        if form.is_valid():
            topic = form.save(commit=False)  # subject
            topic.board = board
            topic.starter = user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=user
            )
            return redirect('topic_posts', pk=board.pk, topic_pk=topic.pk)  # TODO: redirect to the created topic page
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})



def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)  
    topic.views += 1
    topic.save()
    return render(request, 'topic_posts.html', {'topic': topic})


# function based view

@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


from django.views.generic import View

# class based view
# class NewPostView(View):
#     def render(self, request, context=None):
#         return render(request, 'new_post.html', context)

#     def post(self, request, **kwargs):
#         # print(request.POST, request.method, kwargs)
#         topic = get_object_or_404(Topic, board__pk=kwargs["pk"], pk=kwargs["topic_pk"])
#         self.form = PostForm(request.POST)
#         if self.form.is_valid():
#             post = self.form.save(commit=False)
#             post.topic = topic
#             post.created_by = request.user
#             post.save()
#             return redirect('topic_posts', pk=kwargs["pk"], topic_pk=kwargs["topic_pk"])
#         return self.render(request)

#     def get(self, request, **kwargs):
#         self.form = PostForm()
#         topic = get_object_or_404(Topic, board__pk=kwargs["pk"], pk=kwargs["topic_pk"])
#         return self.render(request, context= {'form': self.form, 'topic': topic})
        

from django.views.generic import CreateView, ListView, UpdateView, DeleteView

class NewPostView(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('topic_posts')
    template_name = 'new_post.html'

    def post(self, request, *args, **kwargs):
        topic = get_object_or_404(Topic, board__pk=kwargs["pk"], pk=kwargs["topic_pk"])
        self.form = PostForm(request.POST)
        if self.form.is_valid():
            post = self.form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect('topic_posts', pk=kwargs["pk"], topic_pk=kwargs["topic_pk"])


 
def func():
    pass