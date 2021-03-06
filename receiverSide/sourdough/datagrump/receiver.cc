/* simple UDP receiver that acknowledges every datagram */
#define PKT_SIZE 1800
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <mqueue.h>
#include <unistd.h>

#include <cstdlib>
#include <iostream>
#include <list>
#include <string>

#include "file_descriptor.hh"
#include "socket.hh"
#include "contest_message.hh"

using namespace std;


char buffaray_rec[PKT_SIZE];



int msqid_recv;
// key_t key;

void* receiver(void *parms)
{
string arg0;
  string arg1;
  string arg2;
  string arg3;
  string arg4;
  string arg5;
  string arg6;
  string arg7;

   list<string> arguments = (*(list<string> *)(parms));


  arg0 = arguments.front();
  arguments.pop_front();

  arg1 = arguments.front();
  arguments.pop_front();

  arg2 = arguments.front();
  arguments.pop_front();

  arg3 = arguments.front();
  arguments.pop_front();

  arg4 = arguments.front();
  arguments.pop_front();

  arg5 = arguments.front();
  arguments.pop_front();

  arg6 = arguments.front();
  arguments.pop_front();
    
  arg7 = arguments.front();
  arguments.pop_front();


  // int argc = arguments.size();

  struct mq_attr attr;

  attr.mq_msgsize = PKT_SIZE;
  attr.mq_flags = 0;
  attr.mq_maxmsg = 10;

  // "/89898"
  if ((msqid_recv = mq_open(arg7.c_str(),O_RDWR | O_CREAT, 0664, &attr)) == -1) {
      perror("failed to create the msgQ 89898 in m_open");
      exit(1);
  }
   /* check the command-line arguments */
  if ( arg4 == "0" ) { /* for sticklers */
    perror("RECV: command line arg fail");
    abort();
  }

  // if ( argc != 2 ) {
  //   cerr << "Usage: " << arg0 << " PORT" << endl;
  //   return (void *)EXIT_FAILURE;
  // }

  /* create UDP socket for incoming datagrams */
  //FileDescriptor fd(12341);
  // cerr << fd.to_string();
  UDPSocket socket;

  /* turn on timestamps on receipt */
  socket.set_timestamps();
  /* "bind" the socket to the user-specified local port number */
  socket.bind( Address( "::0", arg4 ) );

  cerr << "Listening on " << socket.local_address().to_string() << endl;

  uint64_t sequence_number = 0;
    fsync(1);

  /* Loop and acknowledge every incoming datagram back to its source */
  while ( true ) {
    const UDPSocket::received_datagram recd = socket.recv();
    ContestMessage message = recd.payload;

    memset(buffaray_rec, 0, sizeof(PKT_SIZE));
    std::size_t length = message.to_stringOnly().copy(buffaray_rec,recd.payload.size(),0);

    if (mq_send(msqid_recv, buffaray_rec, length, 0) == -1) /* +1 for '\0' */
       perror("error in msgsnd");

    /* assemble the acknowledgment */
    message.transform_into_ack( sequence_number++, recd.timestamp );

    /* timestamp the ack just before sending */
    message.set_send_timestamp();

    /* send the ack */
    socket.sendto( recd.source_address, message.to_string() );
  }
  return EXIT_SUCCESS;
}

