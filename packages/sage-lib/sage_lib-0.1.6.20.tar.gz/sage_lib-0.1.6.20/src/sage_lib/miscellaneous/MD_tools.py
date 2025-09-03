try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import copy
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing copy: {str(e)}\n")
    del sys


try:
    from time import time
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing copy: {str(e)}\n")
    del sys

class atomic_diffusion_tools(object):
    """

    """

    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Initialize the MolecularDynamicBuilder object.

        Args:
            file_location (str, optional): File location of the input data.
            name (str, optional): Name of the simulation.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(name=name, file_location=file_location)

    def _get_max_displacement(self, containers):
        ''' parses displacements from a atoms trajectory (list),
            PBC are accounted for if crossings are reasonably captured
            (translations larger than half the box length will lead to errors)
            input:   atoms    = list of atoms object
            output:  displ    = list of np.arrays containing the displacement
                                vector for each atoms object (accounting for PBC)
                     dpos_max = array giving the maximum displacement of each
                                atom (accounting for PBC)
        '''
        #parse final displacement
        pos0, pos_b = containers[0].AtomPositionManager.atomPositions_fractional, containers[0].AtomPositionManager.atomPositions_fractional
        dpos_max = np.zeros((pos0[:,0].size))
        vec_t = np.zeros((pos0[:,0].size,3))
        displ = []
        for i in range(0,len(containers)):
            # calculate scaled displacement
            pos_c = containers[0].AtomPositionManager.atomPositions_fractional
            vec_c = self._correct_vec(pos_c-pos_b)
            vec_t += vec_c
            pos_b = pos_c
            # scan maximum displacement
            vec_tr = np.dot(vec_t, containers[i].AtomPositionManager.get_cell() )
            dpos = np.linalg.norm((vec_tr),axis=1)
            dpos_max = (np.transpose(np.vstack((dpos_max,dpos)))).max(axis=1)
            # accumulate displacement
            displ.append(vec_tr)

        displ = np.array(displ)
        return(displ,dpos_max)

    def _correct_vec(self, vec):
        ''' correct vectors in fractional coordinates
            (assuming vectors minimal connection between 2 points)
        '''
        vec[np.where(vec >= 0.5)] -= 1.0
        vec[np.where(vec < -0.5)] += 1.0
        return(vec)

    def _calc_current_einstein_time_averaged(self, containers, charge_dict, lag, atompair=[3, 3], sparsification=10):
        ''' calculate the Einstein formulation of the current correlation averaged
            over a lag time of selected atom types from a list of atoms objects
            input:  atoms = list of atoms objects
                  charges = charges in a dictionary for use
                    lag   = ratio of trajectory length giving lagtime over which
                            to average
                    sparsification = distance between images we want to do the windowing with
            output: qmsd   = dictionary for all atom-types
                            np.array of dimensions (len(atoms),4)
                            containing x,y,z and norm(xyz) of the type-msd
                            for each atoms object
                            charge means square displacement
                    qd    = charge displacement
        '''
        
        length = int(len(containers)*lag) #images using for averaging
        inds, qmsd, charges = {'full': range(len(containers[0].AtomPositionManager.atomPositions))}, {'full': np.zeros((length, 4))}, containers[0].AtomPositionManager.get_atomic_numbers()
        charges = np.array([charge_dict[el] for el in charges])
        qd = {'full': np.zeros((length, 4))}
        inds.update({f"{atompair[0]}_{atompair[1]}": np.array(np.where(containers[0].AtomPositionManager.get_atomic_numbers() == atompair[0])[0].tolist() +\
                                    np.where(containers[0].AtomPositionManager.get_atomic_numbers() == atompair[1])[0].tolist())})
        print(inds)
        qmsd.update({f"{atompair[0]}_{atompair[1]}":np.zeros((length, 4))})
        qd.update({f"{atompair[0]}_{atompair[1]}": np.zeros((length, 4))})
        qmsd_corr = {atompair[0]: np.zeros(length), atompair[1]: np.zeros(length)}
        ###################
        atypes = np.unique(containers[0].AtomPositionManager.get_atomic_numbers())
        for atype in atypes:
            qmsd.update({atype: np.zeros((length, 4))})
            qd.update({atype: np.zeros((length, 4))})
            inds.update({atype: np.where(containers[0].AtomPositionManager.get_atomic_numbers() == atype)[0]})
        sampling_start_list = range(0,len(containers)+1-length,sparsification)

        for i in sampling_start_list:
            displ, dpos_max = self._get_max_displacement(containers[i:i+length])
            step_save = {}
            for dtyp in qmsd:
                tqd = self._displ2qd(displ, inds[dtyp], charges) #[charges[i] for i in range(len(charges)) if i in inds[dtyp]])
                qd[dtyp] += tqd/len(inds[dtyp])
                qmsd[dtyp] += tqd**2.0/len(inds[dtyp])
                step_save.update({dtyp: tqd}) #save for correlated motion calc
            qmsd_el1_eff, qmsd_el2_eff = self._calc_eff_qmsd(step_save[atompair[0]],step_save[atompair[1]], inds)
            qmsd_corr[atompair[0]] += qmsd_el1_eff
            qmsd_corr[atompair[1]] += qmsd_el2_eff
        qmsd.update(qmsd_corr)

        for dtyp in qmsd: # divide through the number of time averages made
            qmsd[dtyp] /= len(sampling_start_list)
            if dtyp in qd:
                qd[dtyp] /= len(sampling_start_list)
        print(np.shape(qd), np.shape(qmsd))
        return qd, qmsd


    def _calc_eff_angle(self,qd1,qd2):
        ''' qd1, qd2 are arrays [timestep,qd] calculate angle between
        '''
        scalar = qd1[:,0]*qd2[:,0] + qd1[:,1]*qd2[:,1] + qd1[:,2]*qd2[:,2]
        r_qd1_norm = 1./np.linalg.norm(qd1[:,:3],axis=1)
        r_qd2_norm = 1./np.linalg.norm(qd2[:,:3],axis=1)
        scalar = scalar * r_qd1_norm * r_qd2_norm
        angle = np.arccos(scalar)
        return angle

    def _calc_eff_qmsd(self,qd1,qd2, inds):
        ''' qd1, qd2 are arrays [timestep,qd] calculate effective transport between them
            cosine rule based correlation
                qd: q_i*dr_i(t) for every species
        '''
        qmsd1_eff, qmsd2_eff = np.zeros(qd1[:,0].size), np.zeros(qd2[:,0].size)
        corr = qd1[:,0]*qd2[:,0] + qd1[:,1]*qd2[:,1] + qd1[:,2]*qd2[:,2]  # dot product
        qmsd1_eff = (np.linalg.norm(qd1[:,:3], axis=1)**2.0) + corr # (+ sign due to q*factored msd) ???
        qmsd2_eff = (np.linalg.norm(qd2[:,:3], axis=1)**2.0)+ corr
        return qmsd1_eff, qmsd2_eff

    def _displ2qd(self, displ, ind, charges):
        ''' inner function for msd calculation:
            input:  displ = list of per ion xyz-displacements for a
                            series of snapshots
                    ind   = indices of atoms for which to calculate the qmsd
                  charges = dictionary for the charges to use in the qmsd
            output: qmsd   = Einstein formulation of the current correlation
                             np.array(len(atoms),4)
        '''
        qd = []
        for i in range(0,len(displ)):
            q_x = np.sum(charges[ind]*displ[i][ind,0])
            q_y = np.sum(charges[ind]*displ[i][ind,1])
            q_z = np.sum(charges[ind]*displ[i][ind,2])
            q_r = np.linalg.norm(np.array([q_x,q_y,q_z]))
            qd.append([q_x, q_y, q_z, q_r])
        return np.array(qd)

    def _calc_msd_interval(self,containers,interval):
        ''' calculate the Einstein formulation of the current correlation averaged
            over a lag time of selected atom types from a list of atoms objects
            input:  containers = list of containers objects
                 interval = interval between datapionts taken for sample traj (=number of trajs)
            output: msd   = dictionary for all atom-types
                            np.array of dimensions (len(atoms),4)
                            containing x,y,z and norm(xyz) of the type-msd
                            for each containers object atoms
        '''
        from time import time

        tlen = len(containers) - len(containers)%interval
        if tlen%interval != 0:
            raise Exception("%i vs %i : bad interval/ntraj - multiple of trajectory length"%(interval,len(containers)))
        length = len(range(0,tlen,interval))

        atypes = [3,8,17]
        msd, inds = {}, {}
        for atype in atypes:
            msd.update({atype:np.zeros((interval,length,4))})
            inds.update({atype:np.where(containers[0].AtomPositionManager.get_atomic_numbers() == atype)[0]})

        displ_tot, dpos_max = self._get_max_displacement(containers) #complete vec hist
        for i in range(0,interval):
            t0 = time()
            displ = displ_tot[i:tlen:interval] - displ_tot[i] #simple and works
            for atype in atypes:
                msd[atype][i][:,:] = self._displ2msd(displ,inds[atype])
            if (i%200 == 0):
                print("at %i of %i with %.2f sec per calc"%(i,interval,time()-t0))
        return msd

    def _calc_msd_time_averaged(self,containers,atypes,lag, sampling_dist = 10):
        ''' calculate mean square displacement (msd) averaged over
            a lag time of selected atoms types from a list of atoms objects
            input:  atoms = list of atoms objects
                    atype = atom type for which to compute msd
                    lag   = ratio of trajectory length giving lagtime over which
                            to average
            output: msd   = dictionary for all atom-types
                            np.array of dimensions (len(atoms),4)
                            containing x,y,z and norm(xyz) of the type-msd
                            for each atoms object
        '''
        from time import time
        length = int(len(containers)*lag) #images using for averaging
        msd, inds = {}, {}
        for atype in atypes:
            msd.update({atype:np.zeros((length,4))})
            inds.update({atype:np.where(containers[0].AtomPositionManager.get_atomic_numbers() == atype)[0]})
        print(length, len(containers))
        print(f"Averaging over {len(containers)+1-length} configurations")
        sampling_start_list = range(0,len(containers)+1-length,sampling_dist)
        for i in sampling_start_list:
            print(i)
            t0 = time()
            displ, dpos_max = self._get_max_displacement(containers[i:i+length])
            for atype in atypes:
                msd[atype] += self._displ2msd(displ,inds[atype])
            if (i%20 == 0):
                print("at %i of %i with %.2f sec per calc"%(i,len(containers)-length,time()-t0))
        for atype in atypes:
            msd[atype] /= len(sampling_start_list)
        return msd

    def _displ2msd(self,displ,ind):
        ''' inner function for msd calculation:
            input:  displ = list of per ion xyz-displacements for a
                            series of snapshots
                    ind   = indices of atoms for which to calculate the msd
            output: msd   = mean squared displacement of dimensions (len(atoms),4)
        '''
        msd = []
        for i in range(0,len(displ)):   # loop over all snapshots
            msd_x = np.mean(displ[i][ind,0]*displ[i][ind,0])
            msd_y = np.mean(displ[i][ind,1]*displ[i][ind,1])
            msd_z = np.mean(displ[i][ind,2]*displ[i][ind,2])
            r = np.linalg.norm(displ[i][ind,:],axis=1)
            msd_r = np.mean(r*r)
            msd.append([msd_x,msd_y,msd_z,msd_r])
        return np.array(msd)
     
    def _displ2msd_per_atom(self,displ,ind):
        ''' inner function for msd calculation:
            input:  displ = list of per ion xyz-displacements for a
                            series of snapshots
                    ind   = indices of atoms for which to calculate the msd
            output: msd   = mean squared displacement of dimensions (len(atoms),4)
        '''
        msd = []
        for i in range(0,len(displ)):
            msd_per_at=[]
            for ii in range(0,len(displ[0])):
                msd_x = np.mean(displ[i][ii,0]*displ[i][ii,0])
                msd_y = np.mean(displ[i][ii,1]*displ[i][ii,1])
                msd_z = np.mean(displ[i][ii,2]*displ[i][ii,2])
                r = np.linalg.norm(displ[i][ii,:])#,axis=1)
                msd_r = np.mean(r*r)
                msd_per_at.append([msd_x,msd_y,msd_z,msd_r])
            msd.append(msd_per_at)
        return(np.array(msd))

    def _disp_per_atom(self,displ,ind):
        ''' Carsten inner function for msd calculation:
            input:  displ = list of per ion xyz-displacements for a
                            series of snapshots
                    ind   = indices of atoms for which to calculate the msd
            output: msd   = mean squared displacement of dimensions (len(atoms),4)
        '''
        dispos = []
        for i in range(0,len(displ)):
            msd_per_at=[]
            for ii in range(0,len(displ[0])):
                msd_x = np.mean(displ[i][ii,0])
                msd_y = np.mean(displ[i][ii,1])
                msd_z = np.mean(displ[i][ii,2])
                #r = np.linalg.norm(displ[i][ii,:])#,axis=1)
                #msd_r = np.mean(r*r)
                msd_per_at.append([msd_x,msd_y,msd_z])
            dispos.append(msd_per_at)
        return(np.array(dispos))

    def _calc_disp_per_atom(self,containers, atype):
        ''' calculates the mean square displacement (msd) of a selected
            atom type from a list of atoms objects
            input:  atoms = list of atoms objects
                    atype = atom type for which to compute msd
            output: msd   = np.array of dimensions (len(atoms),4)
                            containing x,y,z and norm(xyz) of the type-msd
                            for each atoms object
        '''
        ind = range(containers[0].AtomPositionManager.get_atomic_numbers().size)
        if (atype != None):
            ind = np.where(containers[0].AtomPositionManager.get_atomic_numbers() == atype)[0] #isolate type
        displ, dpos_max = self._get_max_displacement(containers)
        msd = self._disp_per_atom(displ,ind)
        return(msd)

    def _calc_msd(self,containers,atype):
        ''' calculates the mean square displacement (msd) of a selected
            atom type from a list of atoms objects
            input:  atoms = list of atoms objects
                    atype = atom type for which to compute msd
            output: msd   = np.array of dimensions (len(atoms),4)
                            containing x,y,z and norm(xyz) of the type-msd
                            for each atoms object
        '''
        ind = range(containers[0].AtomPositionManager.get_atomic_numbers().size)
        if (atype != None):
            ind = np.where(containers[0].AtomPositionManager.get_atomic_numbers() == atype)[0] #isolate type
        displ, dpos_max = self._get_max_displacement(containers)
        msd = self._displ2msd(displ,ind)
        return(msd)

    def _calc_msd_per_atom(self,containers,atype):
        ''' calculates the mean square displacement (msd) of a selected
            atom type from a list of atoms objects
            input:  atoms = list of atoms objects
                    atype = atom type for which to compute msd
            output: msd   = np.array of dimensions (len(atoms),4)
                            containing x,y,z and norm(xyz) of the type-msd
                            for each atoms object
        '''
        ind = range(containers[0].AtomPositionManager.get_atomic_numbers().size)
        if (atype != None):
            ind = np.where(containers[0].AtomPositionManager.get_atomic_numbers() == atype)[0] #isolate type
        displ, dpos_max = self._get_max_displacement(containers)
        msd = self._displ2msd_per_atom(displ,ind)
        return(msd)

    def _accumulate_type_atoms_displ(self,containers,atype,dmin=3.):
        ''' creates a new atoms object from list of atoms objects accumulating
            atom positions for chosen types with minimal displacement dmin
            - this is usefull to visualize where atom migration occurred
            input:  atoms = list of atoms objects
                    atype = atom type selected
                    dmin  = minimal displacement for selection
            output: dens  = atoms object including all positions of atoms
                            fullfilling atype and dmin criteria
        '''
        ind = np.where(containers[0].AtomPositionManager.get_atomic_numbers() == atype)[0] #isolate type
        displ, d_max = self._get_max_displacement(containers)
        ind2 = ind[np.where(d_max[ind] > dmin)[0]] #isolate type-displ
        dens = self._accumulate_atoms_pos(containers,ind2)
        return(dens)

    def _accumulate_atoms_pos(self,containers,ind):
        ''' creates a new atoms object from list of atoms objects accumulating
            atom positions via given indices
            input:  atoms = list of atoms objects
                    ind   = selected atom indices
            output: dens  = atoms object including all positions of selected atoms
        '''
        pos_d, atno = np.zeros((ind.size*len(containers),3)), np.zeros((ind.size*len(containers)))
        # accumulate positions of isolated atoms
        for i in range(0,len(containers)):
            pos = containers[0].AtomPositionManager.atomPositions
            pos_d[i*ind.size:(i+1)*ind.size,:] = pos[ind,:]
            atno[i*ind.size:(i+1)*ind.size] = containers[0].AtomPositionManager.get_atomic_numbers()[ind]
        #create new atoms object
        dens = Atoms(numbers=atno,positions=pos_d,cell=containers[0].AtomPositionManager.get_cell() )
        return(dens)

    def _get_coordination(self,containers,a,b,rcut):
        ''' function to obtain coordination numbers for a list of atom objects:
            input : atoms    = list of atom objects
                    a, b     = atomic numbers between which to obtain the coordination
                    rcut     = cutoff until which to obtain coordination numbers
                    min_freq = minimum share of images for an atom i to be coordinating
                               atom a to be counted into stik_set
            output: cord_dat = numpy array with dimensions (N(a),len(atoms)) giving
                               the coordination of each a in each step
                    cord_set = number of different atoms coordinating atom a across all
                               images
                    stik_dat = mean coordination duration of b around each a
            NOTE: if a = b self-coordination is included
        '''
        types = containers[0].AtomPositionManager.get_atomic_numbers()
        ind_a, ind_b = np.where(types == a)[0], np.where(types == b)[0]
        cord_dat, cord_set, stik_dat = np.zeros((ind_a.size,len(containers))), [set_count() for a in range(0,ind_a.size)], []
        for i in range(0,len(containers)):
            spos, cell = containers[i].AtomPositionManager.atomPositions_fractional, containers[i].AtomPositionManager.get_cell()
            for j in range(0,ind_a.size):
                cord = self.__get_immediate_CN(spos[ind_b,:],spos[ind_a[j],:],cell,rcut)
                cord_dat[j,i] = cord.size
                [cord_set[j].add(cord[c]) for c in range(cord.size)]
        for i in range(0,len(cord_set)):
            ids, counts = cord_set[i].get_count()
            stik_dat.append(np.mean(counts))
        cord_set = np.array([len(cord_set[c]) for c in range(len(cord_set))])
        return(cord_dat,cord_set,np.array(stik_dat))

    def _get_neighbor_inds(self,containers,ind,rcut):
        ''' function to obtain neighbor inds within rcut
            input:  atoms     = ase-atoms-obj
                    ind       = central atom id
                    rcut      = cutoff for which to obtain points within distance
            output: inds      = neighbor ids
        '''
        pos_array = containers[0].AtomPositionManager.atomPositions_fractional
        cell = containers[0].AtomPositionManager.get_cell()
        pos = pos_array[ind,:]
        all_inds = self.__get_immediate_CN(pos_array,pos,cell,rcut)
        neighs = np.setdiff1d(all_inds,[ind],assume_unique=True)
        return(neighs)

    def __get_immediate_CN(self,pos_array,pos,cell,rcut):
        ''' function to calculate distance array (pos_array - pos) and determine
            entries within distance rcut
            input:  pos_array = positions which to calculate distances from
                    pos       = origin position
                    cell      = transformation for distance vectors
                    rcut      = cutoff for which to obtain points within distance
            output: cord      = entries of points in pos_array within distance rcut
        '''
        dvec = self._correct_vec(pos_array-pos)
        dvec = np.dot(dvec,cell)
        dist = np.linalg.norm(dvec,axis=1)
        cord = np.where(dist <= rcut)[0]
        return(cord)

    def _coordination_decay(self,containers,a,b,rcut):
        ''' function to obtain the change/decay of the original coordination for a
            list of atom objects/trajectory:
            input : atoms    = list of atom objects
                    a, b     = atomic numbers between which to obtain the coordination
                    rcut     = cutoff until which to obtain coordination numbers
            output: cord_ = numpy array with dimensions (N(a),len(atoms)) giving
                               the share of the original coordination in each step
            NOTE: if a = b self-coordination is included
        '''
        types = containers[0].AtomPositionManager.get_atomic_numbers()
        ind_a, ind_b = np.where(types == a)[0], np.where(types == b)[0]
        o_set, cord0  = np.zeros((ind_a.size,len(containers))), []
        #set-up initial coordination sets:
        spos, cell = containers[0].AtomPositionManager.atomPositions_fractional, containers[0].AtomPositionManager.get_cell()
        for i in range(0,ind_a.size):
            cord0.append(self.__get_immediate_CN(spos[ind_b,:],spos[ind_a[i]],cell,rcut))
        #obtain overlap of cord0 and cord_i for each timestep i
        for i in range(0,len(containers)):
            spos, cell = containers[i].AtomPositionManager.atomPositions_fractional, containers[i].AtomPositionManager.get_cell()
            for j in range(0,ind_a.size):
                cord = self.__get_immediate_CN(spos[ind_b,:],spos[ind_a[j]],cell,rcut)
                o_set[j,i] = float(np.intersect1d(cord0[j],cord).size)
        return(o_set)

    def _get_velocities_from_positions(self,containers,timestep):
        ''' function to compute velocities from distance difference and timestep
            NOTE that this should only be done for adjacend snapshots - only for
            orthogonal boxes
            input : atoms    = list of atom objects
                    tiemstep = timestep between snapshots
            output: vel      = list of np.arrays containing xyz velocities for N-1 snapshots
        '''
        vel = []
        for i in range(0,len(containers)-1):
            vec = self._correct_vec(containers[i+1].AtomPositionManager.atomPositions_fractional - containers[i].AtomPositionManager.atomPositions_fractional )
            vec = np.dot(vec,containers[i].AtomPositionManager.get_cell())
            vel.append(vec / timestep)
        return(vel)











# containers[0].AtomPositionManager
# containers
# atoms























