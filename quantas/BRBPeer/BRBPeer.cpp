/*
Copyright 2022

This file is part of QUANTAS.
QUANTAS is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
QUANTAS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with QUANTAS. If not, see <https://www.gnu.org/licenses/>.
*/

constexpr char RESET   [] = "\033[0m";
constexpr char RED     [] = "\033[31m";
constexpr char GREEN   [] = "\033[32m";
constexpr char YELLOW  [] = "\033[33m";
constexpr char BLUE    [] = "\033[34m";
constexpr char MAGENTA [] = "\033[35m";
constexpr char CYAN    [] = "\033[36m";

#include "BRBPeer.hpp"
#include <iostream>
#include <cmath>
#include <cstdio>
using namespace std;

int count(vector<string> m){
	int cnt = 0;
	for (auto val : m){
		if (val != "_") cnt++;
	}
	return cnt;
}


string getVal(vector<string> v, int thresh){
	map<string,int> dict;
	for (auto value : v){
		if (value == "_") continue;
		if (dict.find(value) == dict.end()){
			dict[value] = 1;
		}
		else{
			dict[value] += 1;
		}
	}

	for (auto [val, cnt] : dict){
		if (cnt >= thresh) return val;
	}
	return "";
}

namespace quantas {

	//
	// Example Channel definitions
	//
	BRBPeer::~BRBPeer() {

	}

	BRBPeer::BRBPeer(const BRBPeer& rhs) : Peer<ExampleMessage>(rhs) {
		
	}

	BRBPeer::BRBPeer(long id) : Peer(id) {
		
	}

	void BRBPeer::initParameters(const vector<Peer<ExampleMessage>*>& _peers, json topology, map<string,vector<int>>& term_time) {
		
		if (print==true) cout << "[node] initParams" << endl;

		termination_time = &term_time;

		senderId = topology["sender_id"];
		msgToSend = topology["msgToSend"];
		algorithm = topology["algorithm"];

		n = topology["totalPeers"];
		int t = topology["byzantine"]["total"];

		im_byzantine = false;
		vector<long> v = topology["byzantine"]["list"];
		for (auto val : v){
			if (val == id()){
				im_byzantine = true;
				break;
			}
		}

		print = false;
		if (topology.contains("print")){
			print = topology["print"];
		}

		string ma_type = topology["messageAdversary"]["behavior"];
		int ma_power = topology["messageAdversary"]["power"];

		if (ma_type == "ma1"){
			setMA(n, ma_type, ma_power, {});
		}
		else if (ma_type == "ma2"){
			vector<interfaceId> nodes_blocked = {};
			if (topology.contains("messageAdversary") && topology["messageAdversary"].contains("nodes_blocked")){
				for (auto val : topology["messageAdversary"]["nodes_blocked"]){
					nodes_blocked.push_back(val);
				}
			}
			setMA(n, ma_type, ma_power, nodes_blocked);
		}
		else if (ma_type == "ma3"){
			setMA(n, ma_type, ma_power, {});
		}

		// bracha 
		echo_threshold = ceil( (float)(n+t+1)/ (float)2);
		ready_threshold = t+1;
		deliver_threshold = 2*t+1;
		send_list.assign(n,"_");
		echo_list.assign(n,"_");
		ready_list.assign(n,"_");


		// opodis
		signatures.assign(n,"_");
        fragments.assign(n,"_");
		signature_threshold = ceil( (float)(n+t+1)/ (float)2 );
		fragments_threshold = topology["delivery_threshold"];
	
	}

	void BRBPeer::performComputation() {
		if (im_byzantine == true){
			byzantineBehavior();
		}
		else{
			if (algorithm == "bracha"){
				bracha();
			}
			else if (algorithm == "opodis_1" || algorithm == "opodis_2t+1" || algorithm == "opodis_t+1"){
				opodis();
			}
			else{
				if (print==true) cout << "Error: correct behavior not defined" << endl;
			}
			
		}
	}

	void BRBPeer::rc_broadcast(ExampleMessage msg, vector<interfaceId> excluded){
		double ms = broadcast_MA(msg, excluded);
		msgs_sent += ms;

		if (msg.source == id()){
			if (algorithm == "bracha" && print==true) cout << GREEN << "[node_" << id() << "] broadcasting: " << br_str(msg) << RESET << endl;
			if ((algorithm == "opodis_1" || algorithm == "opodis_2t+1") && print==true) cout << GREEN << "[node_" << id() << "] broadcasting: " << op_str(msg) << RESET << endl;
		}
	}

	// senderId != sourceId
	// senderId is the id of the node from which the message was received
	void BRBPeer::propagate(ExampleMessage msg, interfaceId senderId){
		if (msg.source == id()) return; // if the source is me, then i already propagated it
		if (received_msgs_set.count(msg.id) == 0) {
			received_msgs_set.insert(msg.id);
			if (algorithm == "bracha" && print == true)
				cout << YELLOW << "[node_" << id() << "] propagating: " << br_str(msg) << RESET << endl;
			if ((algorithm == "opodis_1" || algorithm == "opodis_2t+1") && print == true)
				cout << YELLOW << "[node_" << id() << "] propagating: " << op_str(msg) << RESET << endl;
			rc_broadcast(msg, {id(), msg.source, senderId});
		}
		
		/*
		if (find(received_msgs.begin(), received_msgs.end(), msg.id) == received_msgs.end()){
			received_msgs.push_back(msg.id);
			if (algorithm == "bracha" && print==true) cout << YELLOW << "[node_" << id() << "] propagating: " << br_str(msg) << RESET << endl;
			if ((algorithm == "opodis_1" || algorithm == "opodis_2t+1") && print==true) cout << YELLOW << "[node_" << id() << "] propagating: " << op_str(msg) << RESET << endl;
			rc_broadcast(msg, {id(), msg.source, senderId}); 
		}
		*/
		
	}

	//--------------------------------------------------  BRACHA ALGORITHM  --------------------------------------------------
	

	void BRBPeer::echo_check(){
		// if ready was sent, then no need to send echo
		if (sent_ready == true) return; 

		string val = getVal(echo_list, echo_threshold);
		if (val != ""){
			sent_ready = true;
			ExampleMessage msg;
			msg.source = id();
			msg.type = "ready";
			msg.value = val;
			msg.id = "ready_"+to_string(id());
			rc_broadcast(msg);
		}
	}

	void BRBPeer::ready_check(){
		// if ready was sent, then no need to send echo
		if (sent_ready == true) return; 

		string val = getVal(ready_list, ready_threshold);
		if (val != ""){
			sent_ready = true;
			ExampleMessage msg;
			msg.source = id();
			msg.type = "ready";
			msg.value = val;
			msg.id = "ready_"+to_string(id());
			rc_broadcast(msg);
		}
	}

	void BRBPeer::deliver_check(){
		// if already delivered, then no need to do anything
		if (delivered == true) return; 

		string val = getVal(ready_list, deliver_threshold);
		if (val != ""){
			delivered = true;
			bracha_deliver(val);
		}
	}

	void BRBPeer::bracha_rc_deliver(ExampleMessage msg){
		if (print==true) cout << RED << "[node_" << id() << "] RC-deliver " << br_str(msg) << RESET << endl; 

		// if the message is new then process it
		if (msg.type == "send" && send_list[msg.source] == "_") send_list[msg.source] = msg.value;
		else if (msg.type == "echo" && echo_list[msg.source] == "_") echo_list[msg.source] = msg.value;
		else if (msg.type == "ready" && ready_list[msg.source] == "_") ready_list[msg.source] = msg.value;
		// if the message is not new, then do nothing
		else return;
		
		if (msg.type == "send" && sent_echo==false){
			ExampleMessage echo_msg;
			echo_msg.source = id();
			echo_msg.type = "echo";
			echo_msg.value = msg.value;
			echo_msg.id = "echo_"+to_string(id());
			sent_echo = true;
			rc_broadcast(echo_msg);
		}
		else if (msg.type == "echo"){
			echo_list[msg.source] = msg.value;
		}
		else if (msg.type == "ready"){
			ready_list[msg.source] = msg.value;
		}
	}

	void BRBPeer::bracha_broadcast(string val){
		ExampleMessage msg;
		msg.source = id();
		msg.type = "send";
		msg.value = val;
		msg.id = "send_"+to_string(id());
		rc_broadcast(msg);
	}

	void BRBPeer::bracha_deliver(string val){
		if (print==true) cout << "[node_" << id() << "] deliver --> " << val << endl;
		(*termination_time)["0"][id()] = getRound();
	}

	void BRBPeer::bracha() {

		// for the sender only
		if (id() == senderId && getRound() == 0){
			if (print==true) cout << "[node_" << id() << "] starting broadcast as sender" << endl;
			for (int i=0; i<msgToSend; i++){
				bracha_broadcast(std::to_string(i));
			}
		}

		while (!inStreamEmpty()){
			Packet<ExampleMessage> MSG = popInStream();
			ExampleMessage msg = MSG.getMessage();
			propagate(msg, MSG.sourceId());
			bracha_rc_deliver(msg);
		}

		if (print==true) cout << "[node_" << id() << "]" << endl;
		if (print==true) cout << "send_list: " << vec_to_string(send_list) << endl;
		if (print==true) cout << "echo list:" << vec_to_string(echo_list) << endl;
		if (print==true) cout << "ready list:" << vec_to_string(ready_list) << endl;

		if (delivered==false){
			echo_check();
			ready_check();
			deliver_check();
		}
		if (print==true) cout << endl;
	}
	//------------------------------------------------------------------------------------------------------------------------

	//--------------------------------------------------  OPODIS ALGORITHM  --------------------------------------------------
	void BRBPeer::signature_check(){
		if (delivered == true) return;		
		if (count(signatures) >= signature_threshold) enough_signature = true;
		if (enough_signature == true && count(fragments) >= fragments_threshold){
			sent_boundle = true;
			delivered = true;
			for (int i=0; i<n; i++){
				ExampleMessage msg;
				msg.source = id();
				msg.destination = i;
				msg.C = commit;
				msg.frag_a = id();
				msg.frag_b = i;
				msg.type = "bundle";
				msg.id = "bundle_complete"+to_string(msg.source)+"_"+to_string(msg.destination);
				rc_broadcast(msg);
			}
			opodis_deliver(commit);
		}
	}
	
	void BRBPeer::opodis_rc_deliver(ExampleMessage msg){

		// if the message is not new, then don't do anything
		if (received_msgs_set.count(msg.id)) return;
		//if ( find(received_msgs.begin(), received_msgs.end(), msg.id) != received_msgs.end() ) return;
		

		// if the message is new, save it so we don't use it again
		if (print==true) cout << RED << "[node_" << id() <<"] received: " << op_str(msg) << RESET << endl;
		received_msgs_set.insert(msg.id);
		//received_msgs.push_back(msg.id);
		commit = msg.C;

		if (msg.type == "send" && msg.source == senderId && sent_forward_ps==false){
			sent_forward_ps = true;
			sent_forward = true;
			fragments[id()] = msg.frag_a;
			for (auto i : msg.signs) signatures[i] = to_string(i);
			if (print==true) cout << "  -->f: " << vec_to_string(fragments) << "  -->s: " << vec_to_string(signatures) << endl;

			for (int i=0; i<n; i++){
				ExampleMessage new_msg;
				new_msg.source = id();
				new_msg.destination = i;
				new_msg.C = msg.C;
				new_msg.frag_a = msg.frag_a;
				new_msg.signs.push_back(senderId);
				new_msg.signs.push_back(id());
				new_msg.type = "forward";
				new_msg.id = "forward_known_"+to_string(new_msg.source)+"_"+to_string(new_msg.destination);
				rc_broadcast(new_msg);
			}
		}

		if (msg.type == "forward"){
			for (auto i : msg.signs) signatures[i] = to_string(i);
			if (msg.frag_a != "_") fragments[msg.source] = msg.frag_a;
			if (sent_forward == true && print==true) cout << "  -->f: " << vec_to_string(fragments) << "  -->s: " << vec_to_string(signatures) << endl;
			if (sent_forward == false){
				sent_forward = true;
				signatures[id()] = to_string(id());
				if (print==true) cout << "  -->f: " << vec_to_string(fragments) << "  -->s: " << vec_to_string(signatures) << endl;

				for (int i=0; i<n; i++){
					ExampleMessage new_msg;
					new_msg.source = id();
					new_msg.destination = i;
					new_msg.C = msg.C;
					new_msg.signs.push_back(senderId);
					new_msg.signs.push_back(id());
					new_msg.type = "forward";
					new_msg.id = "forward_unknown_"+to_string(new_msg.source)+"_"+to_string(new_msg.destination);
					rc_broadcast(new_msg);
				}
			} 
		}

		if (msg.type == "bundle"){
			enough_signature = true;
			fragments[msg.source] = msg.frag_a;
			if ( (sent_boundle == true || msg.frag_b == "_" ) && print==true) cout << "  -->f: " << vec_to_string(fragments) << "  -->s: " << vec_to_string(signatures) << endl;
			if (sent_boundle==false && msg.frag_b != "_"){
				fragments[id()] = msg.frag_b;
				if (print==true) cout << "  -->f: " << vec_to_string(fragments) << "  -->s: " << vec_to_string(signatures) << endl;

				for (int i=0; i<n; i++){
					ExampleMessage new_msg;
					new_msg.source = id();
					new_msg.destination = i;
					new_msg.C = msg.C;
					new_msg.frag_a = msg.frag_b;
					new_msg.signs.push_back(senderId);
					new_msg.signs.push_back(id());
					new_msg.type = "bundle";
					new_msg.id = "bundle_"+to_string(new_msg.source)+"_"+to_string(new_msg.destination);
					rc_broadcast(new_msg);
				}
			}
		}

	}    

	void BRBPeer::opodis_broadcast(string val){
		commit = val;
		for (int i=0; i<n; i++){
			ExampleMessage msg;
			msg.source = id();
			msg.destination = i;
			msg.C = val;
			msg.frag_a = val[i];
			msg.signs.push_back(id());
			msg.type = "send";
			msg.id = "send_"+to_string(msg.source)+"_"+to_string(msg.destination);
			rc_broadcast(msg);
		}
	}     
	
	void BRBPeer::opodis_deliver(string val){
		if (print==true) cout << BLUE << "[node_" << id() << "] Delivered" << RESET << endl;
		(*termination_time)["0"][id()] = getRound();
	} 

	void BRBPeer::opodis(){
		// for the sender only
		if (id() == senderId && getRound() == 0){
			if (print==true) cout << "[node_" << id() << "] starting broadcast as sender" << endl;
			string val = "Everygreatjourneybeginswithasinglestepandcouragegrowsstrongerwitheachsmallvictory";
			for (int i=0; i<msgToSend; i++){
				opodis_broadcast(val);
			}
		}

		while (!inStreamEmpty()){
			Packet<ExampleMessage> MSG = popInStream();
			ExampleMessage msg = MSG.getMessage();
			//if (print==true) cout << "[node_" << id() << "] received: " << op_str(msg) << " <--- " << MSG.sourceId() << endl;
			if (msg.destination != id()) propagate(msg, MSG.sourceId());
			if (msg.destination == id()) opodis_rc_deliver(msg);
		}
		signature_check();
		if (print==true) cout << "[node_" << id() << "]" << endl;
		if (print==true) cout << "fragments: " << vec_to_string(fragments) << endl;
		if (print==true) cout << "signatures: " << vec_to_string(signatures) << endl;
		if (print==true) cout << endl;
	}
	//------------------------------------------------------------------------------------------------------------------------

	// Byzantine behavior can be defined here
	void BRBPeer::byzantineBehavior() {
		// stay silent
		if (print==true) cout << "[node_" << id() << "] ..." << endl;
	}

	void BRBPeer::endOfRound(const vector<Peer<ExampleMessage>*>& _peers) {
		double tot = 0;
		double round = 0;
		for (auto basePeerPtr : _peers) {
			BRBPeer* peer = static_cast<BRBPeer*>(basePeerPtr);
			round += peer->msgs_sent - peer->msgs_sent_prev;
			tot += peer->msgs_sent;
			peer->msgs_sent_prev = peer->msgs_sent;
		}
		if (print==true) cout << endl << BLUE << "End of round " << getRound() << "   msgs_sent_round: " << round << "  tot_msgs_sent: " << tot << RESET << endl;
		//cout << BLUE << "End of round " << getRound() << "   msgs_sent_round: " << round << "  tot_msgs_sent: " << tot << endl;
	}

	Simulation<quantas::ExampleMessage, quantas::BRBPeer>* generateSim() {
        
        Simulation<quantas::ExampleMessage, quantas::BRBPeer>* sim = new Simulation<quantas::ExampleMessage, quantas::BRBPeer>;
        return sim;
    }
}