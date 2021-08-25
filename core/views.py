from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from core.models import Friend,Group,Debt,Event
from django.contrib.auth.models import User
# Create your views here.
from .forms import GroupForm,GroupFormAddMember,EventForm,SettelmentForm
from django.http import HttpResponse

def minOf2(x, y):
    return x if x < y else y

def debts_converter(net_amount_dict,debts_list):
    max_amount=0
    min_amount=0
    for person_net_amount in net_amount_dict:
        if net_amount_dict[person_net_amount] > max_amount:
            max_key = person_net_amount
            max_amount = net_amount_dict[person_net_amount]
        if net_amount_dict[person_net_amount ] < min_amount:
            min_key = person_net_amount
            min_amount = net_amount_dict[person_net_amount]
    if max_amount < 0.001 and min_amount > -0.001:
        return 0
    amount = minOf2(-min_amount, max_amount)
    net_amount_dict[max_key] -= amount
    net_amount_dict[min_key] += amount
    debts_list.append([min_key,max_key,amount])
    debts_converter(net_amount_dict,debts_list)


def index(request):
    username=request.user.username
    return render(request, 'core/home.html', {'username': username})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

def friendsPage(request):
    a = Friend.objects.filter(user1 = request.user)
    b= Friend.objects.filter(user2 = request.user)
    all_users = User.objects.all()
    friends_list=[]
    not_friends_list=[]
    for c in a:
        friends_list.append(c.user2)
    for c in b:
        friends_list.append(c.user1)
    for user in all_users:
        if ( user not in friends_list ) and user!=request.user:
            not_friends_list.append(user)
    return render(request,'core/friendsPage.html',{'friends_list':friends_list , 'not_friends_list':not_friends_list})

def addFriend(request,friendId):
    if(request.user.id!=friendId):
        Friend.objects.get_or_create(user1_id=request.user.id,user2_id = friendId)
    return redirect('core:friendsPage')


def GroupFormView(request):
    messages = []
    if  request.method == 'POST':
        form=GroupForm(request.POST)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.groupAdmin=request.user
            a = Group.objects.filter(groupName = instance.groupName,groupAdmin = instance.groupAdmin)
            if ( not a ):
                instance.save()
                b=Friend.objects.filter(user1=instance.groupAdmin,user2=instance.member)
                c=Friend.objects.filter(user2=instance.groupAdmin,user1=instance.member)
                if ( (not b) and (not c)):
                    friend_temp = Friend(user1=instance.groupAdmin,user2=instance.member)
                    friend_temp.save() 
                return redirect('core:friendsPage')
            else:
                messages= ['Cannot create group with this name']
                print(messages[0])
                return render(request,'core/groupCreate.html',{'form':form , 'messages':messages})
        else:
            print("Form is invalid")
    else:
        form=GroupForm()

    return render(request,'core/groupCreate.html',{'form':form , 'messages':messages})


def groupsPage(request):
    a = Group.objects.filter(member = request.user)
    b= Group.objects.filter(groupAdmin = request.user)
    groups_list=[]
    group_names = []
    for c in a:
        if not ( c.groupName in group_names):
            groups_list.append(c)
            group_names.append(c.groupName)       
    for c in b:
        if not ( c.groupName in group_names):
            groups_list.append(c)
            group_names.append(c.groupName)  
    return render(request,'core/groupsPage.html',{'groups_list':groups_list })

def addMember(request,pk):
    messages = []
    if  request.method == 'POST':
        form=GroupFormAddMember(request.POST)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.groupAdmin=Group.objects.get(id=pk).groupAdmin
            instance.groupName=Group.objects.get(id=pk).groupName
            a = Group.objects.filter(groupName = instance.groupName,groupAdmin = instance.groupAdmin,member=instance.member)
            if ( (not a) and (instance.groupAdmin != instance.member) ):
                
                GroupMembers = Group.objects.filter(groupName = instance.groupName,groupAdmin = instance.groupAdmin)
                b=Friend.objects.filter(user1=instance.groupAdmin,user2=instance.member)
                c=Friend.objects.filter(user2=instance.groupAdmin,user1=instance.member)
                if ( (not b) and (not c)):
                    friend_temp = Friend(user1=instance.groupAdmin,user2=instance.member)
                    friend_temp.save() 
                for group_member in GroupMembers:
                    b=Friend.objects.filter(user1=instance.member,user2=group_member.member)
                    c=Friend.objects.filter(user2=instance.member,user1=group_member.member)
                    if ( (not b) and (not c)):
                        friend_temp = Friend(user1=instance.member,user2=group_member.member)
                        friend_temp.save()
                instance.save()    
                return redirect('core:groupsPage')
            else:
                messages= ['This member already exits in selected group']
                print(messages[0])
                return render(request,'core/groupAddMember.html',{'form':form , 'messages':messages})
        else:
            print("Form is invalid")
    else:
        form=GroupFormAddMember()

    return render(request,'core/groupAddMember.html',{'form':form , 'messages':messages})

def eventCreate(request):
    messages = []
    if  request.method == 'POST':
        form=EventForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            print(instance)
            if (instance.eventType == 'equal'):
                payers = eval(instance.payers)
                print(payers)
                total_event_paid = 0
                for paid_amount in payers.values():
                    total_event_paid=total_event_paid+paid_amount
                group_objects = Group.objects.filter(groupName = instance.groupName,groupAdmin = instance.groupAdmin)
                totol_members_in_group=1
                group_members_net_amount = { instance.groupAdmin.username : 0 }
                for group_object in group_objects:
                    group_members_net_amount[group_object.member.username] = 0
                    totol_members_in_group +=1
                
                group_initial_debts = Debt.objects.filter(groupName = instance.groupName,groupAdmin = instance.groupAdmin)
                print(group_initial_debts)
                for group_initial_debt in group_initial_debts:
                    group_members_net_amount[group_initial_debt.user1.username]  = -float(group_initial_debt.amount)
                    group_members_net_amount[group_initial_debt.user2.username]  =  float(group_initial_debt.amount)
                group_initial_debts.delete()
                print(group_members_net_amount) 
                for payer in payers:
                    group_members_net_amount[payer] = group_members_net_amount[payer] + payers[payer]
                each_person_amount = total_event_paid/totol_members_in_group 
                for person in group_members_net_amount:
                    group_members_net_amount[person] = group_members_net_amount[person] - float(each_person_amount)
                print(group_members_net_amount)

                debts_list =[]
                debts_converter(group_members_net_amount,debts_list)
                print(debts_list)

                for debt in debts_list:
                    user1= User.objects.get(username =debt[0])
                    user2= User.objects.get(username =debt[1])
                    debt_temp = Debt(groupName=instance.groupName,groupAdmin=instance.groupAdmin,user1=user1,user2=user2,amount = debt[2])
                    debt_temp.save()
            return redirect('core:home')
        else:
            print("Form is invalid")
    else:
        form=EventForm(request.POST)

    return render(request,'core/addEvent.html',{'form':form , 'messages':messages})

 
def debts(request):
    debts_of_user = Debt.objects.filter(user1 = request.user) | Debt.objects.filter(user2 = request.user)
    return render(request,'core/debts.html',{'debts_of_user':debts_of_user })


def settle(request,pk):
    debt = Debt.objects.get(id = pk)
    if  request.method == 'POST':
        form=SettelmentForm(request.POST)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.groupName=debt.groupName
            instance.groupAdmin=debt.groupAdmin
            instance.user1 = debt.user1
            instance.user2 = debt.user2
            instance.save()
            debt.amount -= instance.amount 
            debt.save()
            return redirect('core:home')
        else:
            print("Form is invalid")
    else:
        form=SettelmentForm()

    return render(request,'core/settle.html',{'debt':debt,'form':form })