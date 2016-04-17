# gossamer
Web-like chat network
------------------------------------------

starting 'seed' / server

each client connects to a number of other clients

send <address>|<     encrypted     >
               <address>|<encrypted>
	etc... onion routing


seed stores public key and username, client stores private key
seed verifies on client joining

clients store only nicknames and direction

network-wide encryption layer using server's key
each node has induvidual encryption key
vote new users in
