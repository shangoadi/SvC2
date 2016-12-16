/* UDP sender for congestion-control contest */
#define PKT_SIZE 1800
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <string.h>
#include <cstdlib>
#include <iostream>
#include <mqueue.h>
#include "socket.hh"
#include "contest_message.hh"
#include "controller.hh"
#include "poller.hh"

using namespace std;
using namespace PollerShortNames;


char buffarray[PKT_SIZE];

int msqid;
// key_t key;
struct mq_attr  obuf;

/* simple sender class to handle the accounting */
class DatagrumpSender
{
private:
  UDPSocket socket_;
  Controller controller_; /* your class */

 

  uint64_t sequence_number_; /* next outgoing sequence number */

  /* if network does not reorder or lose datagrams,
     this is the sequence number that the sender
     next expects will be acknowledged by the receiver */
  uint64_t next_ack_expected_;
  
  void bindlocalIP( void );
  void send_datagram( void );
  void got_ack( const uint64_t timestamp, const ContestMessage & msg );
  bool window_is_open( void );

public:
  DatagrumpSender( const char * const host, const char * const port,
		   const bool debug, const char * const localIP ,
       const char * const localport);
  int loop( void );
};

int main( int argc, char *argv[] )
{
    struct mq_attr attr;

    attr.mq_msgsize = PKT_SIZE;
    attr.mq_flags = 0;
    attr.mq_maxmsg = 10;

    if ((msqid = mq_open("/68681", O_RDWR, 0664, &attr)) == -1) { /* connect to the queue */
        perror("unable to connect to 68681 in msgget()");
        exit(1);
    }


   /* check the command-line arguments */
  if ( argc < 1 ) { /* for sticklers */
    abort();
  }

  bool debug = false;
  if ( argc == 4 and string( argv[ 3 ] ) == "debug" ) {
    debug = true;
  } else if ( argc == 3 ) {
    /* do nothing */
  }
   else if ( argc == 5 ) {
    
  } else if ( argc == 6 ) {
    
  } else {
    cerr << "Usage: " << argv[ 0 ] << " HOST PORT [debug] LOCALIP LOCALPORT" << endl;
    return EXIT_FAILURE;
  }

  /* create sender object to handle the accounting */
  /* all the interesting work is done by the Controller */
  DatagrumpSender sender( argv[ 1 ], argv[ 2 ], debug ,argv[4], argv[5]);
  
  return sender.loop();
}

DatagrumpSender::DatagrumpSender( const char * const host,
				  const char * const port,
				  const bool debug , const char * const localIP,
          const char * const localport)
  : socket_(),
    controller_( debug ),
    sequence_number_( 0 ),
    next_ack_expected_( 0 )
{
  /* turn on timestamps when socket receives a datagram */
  socket_.set_timestamps();
  /* "bind" the socket to the user-specified local port number */
  socket_.bind( Address( localIP, localport ) );

  /* connect socket to the remote host */
  /* (note: this doesn't send anything; it just tags the socket
     locally with the remote address */
  socket_.connect( Address( host, port ) );  
  
  cerr << "Sending to " << socket_.peer_address().to_string() << endl;
}

void DatagrumpSender::got_ack( const uint64_t timestamp,
			       const ContestMessage & ack )
{
  if ( not ack.is_ack() ) {
    throw runtime_error( "sender got something other than an ack from the receiver" );
    
  }

  /* Update sender's counter */
  next_ack_expected_ = max( next_ack_expected_,
			    ack.header.ack_sequence_number + 1 );

  /* Inform congestion controller */
  controller_.ack_received( ack.header.ack_sequence_number,
			    ack.header.ack_send_timestamp,
			    ack.header.ack_recv_timestamp,
			    timestamp );

}

// void DatagrumpSender::send_datagram( void )
// {

// }

void DatagrumpSender::send_datagram( void )
{
  /* All messages use the same dummy payload */
  // static const string dummy_payload( 1424, 'x' );


  int receiveLength = mq_receive(msqid, buffarray, PKT_SIZE, NULL);
  if(receiveLength == -1)
  {
    cerr << "Failed in mq_receive";
  }
  

  string aNiceString(buffarray, receiveLength);
  ContestMessage cm( sequence_number_++, aNiceString);
  
  cm.set_send_timestamp();
  socket_.send( cm.to_string() );
  //cerr << cm.to_string() <<"\n";
  /* Inform congestion controller */
  controller_.datagram_was_sent( cm.header.sequence_number,
				 cm.header.send_timestamp );
  
}



bool DatagrumpSender::window_is_open( void )
{
  return sequence_number_ - next_ack_expected_ < controller_.window_size();
}

int DatagrumpSender::loop( void )
{
  /* read and write from the receiver using an event-driven "poller" */
  Poller poller;

  /* first rule: if the window is open, close it by
     sending more datagrams */
  poller.add_action( Action( socket_, Direction::Out, [&] () {
	/* Close the window */
	while ( window_is_open() ) {
	  send_datagram();
	}
	return ResultType::Continue;
      },
      /* We're only interested in this rule when the window is open */
      [&] () { return window_is_open(); } ) );

  /* second rule: if sender receives an ack,
     process it and inform the controller_
     (by using the sender's got_ack method) */
  poller.add_action( Action( socket_, Direction::In, [&] () {
	const UDPSocket::received_datagram recd = socket_.recv();
	const ContestMessage ack  = recd.payload;
  
	got_ack( recd.timestamp, ack );
	return ResultType::Continue;
      } ) );

  /* Run these two rules forever */
  while ( true ) {
    const auto ret = poller.poll( controller_.timeout_ms() );
    if ( ret.result == PollResult::Exit ) {
      return ret.exit_status;
    } else if ( ret.result == PollResult::Timeout ) {
      /* After a timeout, send one datagram to try to get things moving again */
      send_datagram();
    }
  }
}
