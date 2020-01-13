/*
 chat channel window/tab javascript functions, for index.html and its inChannels[] array

 Since this modifies the dispatcher array, is loaded asynchronously from index-ws-dispatcher.js.

 This file is part of the Java Settlers Web App (JSWeb).

 This file Copyright (C) 2017,2020 Jeremy D Monin (jeremy@nand.net)

 JSWeb is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 JSWeb is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with JSWeb.  If not, see <https://www.gnu.org/licenses/>.
 */

// Message handlers; see bottom of file for ChatChannel object and inChannels[] entries //

function handleChannelJoin(mData)
{
    var chObj = inChannels[mData.chName];
    if (chObj)
	chObj.handleJoin(mData.memberName);
}

function handleChannelMembers(mData)
{
    var chObj = inChannels[mData.chName];
    if (chObj)
	chObj.handleMembers(mData.members);
}

function handleChannelText(mData)
{
    var chObj = inChannels[mData.chName];
    if (chObj)
	chObj.handleText(mData.memberName, mData.text);
}

function handleLeaveChannel(mData)
{
    var chObj = inChannels[mData.chName];
    if (chObj)
	chObj.handleLeave(mData.memberName);
}

function sendLine(chDoc)
{
    if (! chDoc)
	return;
    if (wsConn == null)
    {
	alert("Not connected.");
	return;
    }

    var chatObj = chDoc.soc_chat_obj;
    if (! chatObj)
	return;
    var txfield = chDoc.forms.send.txt;
    var txt = txfield.value.trim();
    if (0 == txt.length)
	return;

    txfield.value = "";
    wsConn.send(JSON.stringify({chText:{chName: chatObj.chName, text: txt}}));
}

// Top-level UI and ChatChannel object //

function ChatChannel(chName)
{
    this.chName = chName;
    this.chMembers = new Set();
    // newChannelWindow sets this.chWindow, and sets chWindow.document.soc_chat_obj to this
    // handleMembers sets this.membersJQ and .messagesJQ: jquery objs for member list, chat message divs
    this.cliJoined = false;  // obj & new window must be created from dblclick handler, not server's chJoin
    this.sentLeaveMsg = false;  // flag for closeChannelWindow
    this.handleJoin = function(memberName)
    {
	// if we're in that channel, add person to member list there
	// otherwise if mData.memberName is us, open a chat channel window
	// and expect channelmembers message soon
	console.log("chch handleJoin: got here, cliJoined is " + this.cliJoined);
	if ((memberName == nickname) && ! this.cliJoined)
	{
	    var chBody = this.chWindow.document.body;
	    // inline styles because separate css for js newDiv.className was being ignored
	    chBody.style.height = '100%'; chBody.style.margin = '3px';
	    chBody.innerHTML = '<div style="float:right; min-width: 130px; padding: 3px;"><div id="members" style="position: fixed; margin: 3px; width: max-content;"></div></div>'
		+ '<div style="display: flex; flex-flow: column; height: 100%;">'
		+ '<div id="header" style="flex: 0 1 auto;">' // = flex-grow:0,flex-shrink:1,flex-basis:auto
		+ 'Chat Channel: ' + chName + '<HR noshade></div>'
		+ '<div id="messages" style="flex: 1 1 auto; overflow: auto;"></div>'
		+ '<div id="send" style="flex: 0 1 auto; margin: 3px;">'
		+ '<form name="send" action="javascript:window.opener.sendLine(window.document);void(0);" autocomplete="off">'
		+ '<input name="txt" size=80 autocomplete="off" /> &nbsp; <button type="submit">Send</button>'
		+ '</form></div>'
		+ '</div>'
	    // handleMembers sets up membersJQ, messagesJQ
	    this.cliJoined = true;
	}
	if (! (this.cliJoined && this.membersJQ))
	    return;
	if (! this.chMembers.has(memberName))
	{
	    this.chMembers.add(memberName);
	    var mJQ = this.membersJQ;
	    listAddJq(mJQ, memberName, 100);
	    setTimeout(function(){
		var par = mJQ.parent();
		if (mJQ.outerWidth() > par.width())
		    par.width(mJQ.outerWidth());
	      }, 110);
	}
    };
    this.handleMembers = function(memberNames)
    {
	var doc = this.chWindow.document;
	var membersDiv = doc.getElementById("members");
	this.membersJQ = $(membersDiv);
	membersDiv.appendChild(doc.createTextNode("Members:"));
	membersDiv.appendChild(doc.createElement("br"));
	var messagesDiv = doc.getElementById("messages");
	this.messagesJQ = $(messagesDiv);
	var mJQ = this.membersJQ;
	for (var mName of memberNames)
	    if (! this.chMembers.has(mName))
	    {
		this.chMembers.add(mName);
		listAddJq(mJQ, mName, 1);
	    }
	setTimeout(function(){
	    var par = mJQ.parent();
	    if (mJQ.outerWidth() > par.width())
		par.width(mJQ.outerWidth());
	  }, 100);  // wait until fade-ins
	doc.forms.send.txt.focus();
    };
    this.handleLeave = function(memberName)
    {
	if (this.chMembers.has(memberName))
	{
	    this.chMembers.delete(memberName);
	    var mJQ = this.membersJQ;
	    if (mJQ)
	    {
		listRemoveJq(mJQ, memberName, 100);
		setTimeout(function(){
		    var par = mJQ.parent();
		    if (mJQ.outerWidth() < par.width())
			par.width(mJQ.outerWidth());
		}, 110);
	    }
	}
    };
    this.handleText = function(memberName, txt) {
	var mJQ = this.messagesJQ;
	if (! mJQ)
	    return;
	mJQ.append($("<br />"));
	mJQ.append(document.createTextNode(memberName + ": " + txt));
	mJQ.scrollTop(mJQ[0].scrollHeight);
    };
}

function unloadChannelDocEvent(evt)
{
    var chObj = evt.target.soc_chat_obj;
    if (chObj)
	closeChannelWindow(chObj.chName, true);
}

/** New channel name should be html-safe, based on JSettlers allowed names */
function newChannelWindow(chName)
{
    var chObj = new ChatChannel(chName);
    var chWin = window.open("", "soc_chat_" + chName);
    if (chWin)
    {
	chObj.chWindow = chWin;
	chWin.addEventListener("beforeunload", unloadChannelDocEvent);
	chWin.document.write('Chat Channel: ' + chName + '<HR noshade>Joining...');
	chWin.document.close();
	var cLink = chWin.document.createElement("link");
	cLink.rel="stylesheet"; cLink.href="chat-channel.css"; cLink.type="text/css";
	chWin.document.head.appendChild(cLink);
	chWin.document.soc_chat_obj = chObj;
	inChannels[chName] = chObj;
    } else {
	alert("Could not open a new tab to join chat channel.");
    }
}

/* Cleanup when leaving the chat: Called from message dispatcher & from user closing chat window */
function closeChannelWindow(chName, isFromUnloadEvt)
{
    var channelObj = inChannels[chName];
    if (! channelObj)
	return;
    channelObj.chWindow.document.soc_chat_obj = null;
    delete inChannels[chName];  // remove before close(); undefined is OK since we aren't iterating all.
    if (! isFromUnloadEvt)
	channelObj.chWindow.close();
    if (channelObj.cliJoined && ! channelObj.sentLeaveMsg)
    {
	var leaveMsg = { "chLeave": { "chName": chName } };
	sendToServer(leaveMsg);
	channelObj.sentLeaveMsg = true;
    }
}

// Message dispatch //

dispatchTo['chJoin'] = handleChannelJoin;
dispatchTo['chMembers'] = handleChannelMembers;
dispatchTo['chText'] = handleChannelText;
dispatchTo['chLeave'] = handleLeaveChannel;
