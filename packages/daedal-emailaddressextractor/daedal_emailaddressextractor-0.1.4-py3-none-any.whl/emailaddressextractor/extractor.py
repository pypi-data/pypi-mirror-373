# These are the list of modules needed to run the program
import mailbox


# This function will read the MBOX file and search for emaill address
def mboxwriter(mbox, output):
    mbox = mailbox.mbox(mbox)
    file = open(output, 'a')
    for message in mbox:
        file.write(message['from']+'\n')


def createmailerlist(input, emailsonly = 'uniquemails.txt',emailswithcnt = None, dir = None,  invalid = 'invalid email'):
    file_in = open(input,'r')
    addr_lines = file_in.read()
    addr_list = addr_lines.splitlines()
    good_addr_list = []
    unique_addr = [['email  address', 'count']]
    addr_set = set()
    for addr in addr_list:
        if '@' in addr:
            if '<' in addr:
                start = addr.find('<')+1
                end = addr.find('>')
                val = addr[start:end]
            else:
                val = addr
        else:
            val = invalid
        val = val.strip()
        addr_set.add(val)
        good_addr_list.append(val)
    for i in addr_set:
        ctr = good_addr_list.count(i)
        unique_addr.append([i, ctr])
    # store all addresses in files
    if emailswithcnt is not None:
        if dir is None:
            clean_addr = open(emailswithcnt, 'w')
        else:
            clean_addr = open(dir + emailswithcnt, 'w')
        for val in unique_addr:
            clean_addr.write(val[0]+','+str(val[1])+'\n')
        clean_addr.close()
    if dir is None:
        clean_addr = open(emailsonly, 'w')
    else:
        clean_addr = open(dir + emailsonly, 'w')
    for val in addr_set:
        clean_addr.write(val+'\n')
    clean_addr.close()