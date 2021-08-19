#include <stdio.h>
#include <stdlib.h>
#include <linux/input.h>
#include <sys/time.h>

void write_key_event(int code, int value, int fd)
{
  struct input_event key_event;
  
  gettimeofday(&key_event.time, NULL);
  key_event.type = EV_KEY;
  key_event.code = code;
  key_event.value = value;
  write(fd, &key_event, sizeof(key_event));
}

void write_syn(int fd)
{
  struct input_event key_event;

  gettimeofday(&key_event.time, NULL);
  key_event.type = EV_SYN;
  key_event.code = 0;
  key_event.value = 1;
  write(fd, &key_event, sizeof(key_event));
}

int main(int argc, const  char *argv[])
{
  //  write_syn(1);
  for(int i=1; i<argc; i++){
    int num = atoi(argv[i]);
    write_syn(1);
    write_key_event(num, 1, 1);
    write_key_event(num, 0, 1);
    write_syn(1);
  }
  write_syn(1);
  
  exit(EXIT_SUCCESS);
}
